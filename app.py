import os, json, uuid
import requests as http_req
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from config import Config
from models import db, User, Design, Furniture, Booking
from ai_engine import analyze_room, buddy_chat, validate_room_image, ROOM_TYPES, BUDGET_RANGES

app = Flask(__name__)
app.config.from_object(Config)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'auth_page'

ALLOWED = {'png', 'jpg', 'jpeg', 'webp'}

@login_manager.user_loader
def load_user(uid):
    return User.query.get(int(uid))

def allowed(fn):
    return '.' in fn and fn.rsplit('.', 1)[1].lower() in ALLOWED

# ── Pages ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/auth')
def auth_page():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('auth.html')

@app.route('/dashboard')
@login_required
def dashboard():
    designs = Design.query.filter_by(user_id=current_user.id).order_by(Design.created_at.desc()).limit(6).all()
    bookings_count = Booking.query.filter_by(user_id=current_user.id).count()
    designs_count = Design.query.filter_by(user_id=current_user.id).count()
    return render_template('dashboard.html', designs=designs,
                           bookings_count=bookings_count, designs_count=designs_count)

@app.route('/design')
@login_required
def design_page():
    styles = ['Modern', 'Classic', 'Minimal', 'Bohemian', 'Industrial', 'Scandinavian']
    budget_options = [
        {'key': '25k-50k', 'label': '₹25K – ₹50K'},
        {'key': '50k-1l',  'label': '₹50K – ₹1 Lakh'},
        {'key': '1l-2l',   'label': '₹1L – ₹2 Lakh'},
        {'key': '2l-5l',   'label': '₹2L – ₹5 Lakh'},
        {'key': '5l+',     'label': '₹5 Lakh +'},
    ]
    return render_template('design.html', styles=styles,
                           room_types=ROOM_TYPES, budget_options=budget_options)

@app.route('/ar')
@login_required
def ar_page():
    furniture_list = Furniture.query.all()
    return render_template('ar.html', furniture_list=furniture_list)

@app.route('/buddy')
@login_required
def buddy_page():
    return render_template('buddy.html')

@app.route('/bookings')
@login_required
def bookings_page():
    user_bookings = (Booking.query
                     .filter_by(user_id=current_user.id)
                     .order_by(Booking.created_at.desc()).all())
    return render_template('bookings.html', bookings=user_bookings)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# ── Auth API ─────────────────────────────────────────────────────────────────

@app.route('/api/register', methods=['POST'])
def api_register():
    d = request.get_json()
    username, email, password = d.get('username','').strip(), d.get('email','').strip(), d.get('password','')
    if not all([username, email, password]):
        return jsonify(success=False, message='All fields are required.')
    if User.query.filter_by(email=email).first():
        return jsonify(success=False, message='Email already registered.')
    user = User(username=username, email=email, password_hash=generate_password_hash(password))
    db.session.add(user); db.session.commit()
    login_user(user)
    return jsonify(success=True, redirect='/dashboard')

@app.route('/api/login', methods=['POST'])
def api_login():
    d = request.get_json()
    user = User.query.filter_by(email=d.get('email','').strip()).first()
    if user and check_password_hash(user.password_hash, d.get('password','')):
        login_user(user)
        return jsonify(success=True, redirect='/dashboard')
    return jsonify(success=False, message='Invalid email or password.')

# ── Design / AI API ──────────────────────────────────────────────────────────

@app.route('/api/analyze', methods=['POST'])
@login_required
def api_analyze():
    style = request.form.get('style', 'modern')
    room_type = request.form.get('room_type', 'Living Room')
    budget_key = request.form.get('budget', '1l-2l')
    image_path = None

    if 'image' in request.files:
        f = request.files['image']
        if f and allowed(f.filename):
            fname = f"{uuid.uuid4().hex}_{secure_filename(f.filename)}"
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], fname)
            f.save(image_path)

    # Step 1: Validate the image is a room
    if image_path:
        validation = validate_room_image(image_path)
        if not validation.get('is_room', False):
            return jsonify(
                success=False,
                is_room=False,
                message=validation.get('message',
                    'This does not appear to be a room interior. '
                    'Please upload a clear photo of a room.')
            )

    # Step 2: Analyze room with budget constraints
    suggestions = analyze_room(image_path, style, room_type, budget_key)

    # Store in DB
    db_path = os.path.basename(image_path) if image_path else ''
    design = Design(user_id=current_user.id, image_path=db_path,
                    style=style, suggestions_json=json.dumps(suggestions))
    db.session.add(design); db.session.commit()
    return jsonify(success=True, design_id=design.id, suggestions=suggestions)

# ── Buddy / Voice API ────────────────────────────────────────────────────────

@app.route('/api/buddy/chat', methods=['POST'])
@login_required
def api_buddy_chat():
    d = request.get_json()
    message, lang, design_id = d.get('message',''), d.get('lang','en'), d.get('design_id')
    result = buddy_chat(message, lang, current_user.id, design_id)
    if result.get('intent') == 'book' and result.get('furniture_name'):
        fname = result['furniture_name']
        item = Furniture.query.filter(Furniture.name.ilike(f"%{fname}%")).first()
        
        if not item:
            item = Furniture(
                name=fname.title(),
                category="Suggested",
                style_tags="ai-generated",
                price=15000,
                image_url="https://images.unsplash.com/photo-1538688525198-9b88f6f53126?auto=format&fit=crop&w=400",
                description="Custom AI suggested item"
            )
            for sugg in result.get('furniture_suggestions', []):
                if fname.lower() in sugg.get('name', '').lower():
                    item.price = sugg.get('price', item.price)
                    item.image_url = sugg.get('image_url', item.image_url)
                    break
            db.session.add(item)
            db.session.commit()

        bk = Booking(user_id=current_user.id, furniture_id=item.id,
                     design_id=design_id, status='confirmed')
        db.session.add(bk); db.session.commit()
        result['booking_confirmed'] = True
        result['furniture'] = {'id': item.id, 'name': item.name,
                               'price': item.price, 'image_url': item.image_url}
    return jsonify(result)

@app.route('/api/voice/stt', methods=['POST'])
@login_required
def api_stt():
    lang = request.form.get('lang', 'en-IN')
    if 'audio' not in request.files:
        return jsonify(success=False, error='No audio file')
    audio = request.files['audio']
    try:
        headers = {'api-subscription-key': Config.SARVAM_API_KEY}
        files = {'file': (audio.filename or 'audio.wav', audio.stream,
                          audio.content_type or 'audio/wav')}
        data = {'model': 'saarika:v2', 'language_code': lang}
        r = http_req.post('https://api.sarvam.ai/speech-to-text',
                          headers=headers, files=files, data=data, timeout=30)
        return jsonify(success=True, transcript=r.json().get('transcript', ''))
    except Exception as e:
        return jsonify(success=False, error=str(e))

@app.route('/api/voice/tts', methods=['POST'])
@login_required
def api_tts():
    d = request.get_json()
    text, lang = d.get('text', ''), d.get('lang', 'en-IN')
    speaker = {'hi-IN': 'aditya', 'mr-IN': 'aditya', 'en-IN': 'aditya'}.get(lang, 'aditya')
    try:
        headers = {'api-subscription-key': Config.SARVAM_API_KEY,
                   'Content-Type': 'application/json'}
        payload = {'inputs': [text[:500]], 'target_language_code': lang,
                   'speaker': speaker, 'pitch': 0, 'pace': 1.2,
                   'loudness': 1.5, 'speech_sample_rate': 22050,
                   'enable_preprocessing': True, 'model': 'bulbul:v1'}
        r = http_req.post('https://api.sarvam.ai/text-to-speech',
                          headers=headers, json=payload, timeout=30)
        audios = r.json().get('audios', [''])
        return jsonify(success=True, audio=audios[0])
    except Exception as e:
        return jsonify(success=False, error=str(e))

# ── Booking API ──────────────────────────────────────────────────────────────

@app.route('/api/book', methods=['POST'])
@login_required
def api_book():
    d = request.get_json()
    item = None

    # Try finding by furniture_id first
    if d.get('furniture_id'):
        item = Furniture.query.get(d.get('furniture_id'))

    # If not found, try by name (for AI-suggested items from Design Studio)
    if not item and d.get('furniture_name'):
        fname = d['furniture_name']
        item = Furniture.query.filter(Furniture.name.ilike(f"%{fname}%")).first()

        # Auto-create the item if it doesn't exist in catalog
        if not item:
            item = Furniture(
                name=fname.title(),
                category=d.get('furniture_category', 'AI Suggested'),
                style_tags=d.get('furniture_style', 'ai-generated'),
                price=d.get('furniture_price', 0),
                image_url="https://images.unsplash.com/photo-1538688525198-9b88f6f53126?auto=format&fit=crop&w=400",
                description=d.get('furniture_desc', 'AI suggested item from Design Studio')
            )
            db.session.add(item)
            db.session.commit()

    if not item:
        return jsonify(success=False, error='Furniture not found')

    bk = Booking(user_id=current_user.id, furniture_id=item.id,
                 design_id=d.get('design_id'), status='confirmed')
    db.session.add(bk); db.session.commit()
    return jsonify(success=True, booking_id=bk.id,
                   message=f'✅ {item.name} booked successfully!')

@app.route('/api/cancel-booking/<int:bid>', methods=['POST'])
@login_required
def cancel_booking(bid):
    bk = Booking.query.filter_by(id=bid, user_id=current_user.id).first()
    if not bk:
        return jsonify(success=False, error='Booking not found')
    bk.status = 'cancelled'; db.session.commit()
    return jsonify(success=True)

@app.route('/api/furniture')
@login_required
def api_furniture():
    style = request.args.get('style', '')
    q = Furniture.query
    if style:
        q = q.filter(Furniture.style_tags.ilike(f'%{style}%'))
    items = q.all()
    return jsonify([{'id': i.id, 'name': i.name, 'category': i.category,
                     'price': i.price, 'image_url': i.image_url,
                     'description': i.description} for i in items])

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
