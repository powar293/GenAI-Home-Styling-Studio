"""WSGI entry point for Gunicorn (production deployment)."""
from app import app, db
from models import User, Furniture
from werkzeug.security import generate_password_hash
from seed import FURNITURE

# Initialize database and seed on startup
with app.app_context():
    db.create_all()
    # Seed demo user
    if not User.query.filter_by(email='demo@gruha.com').first():
        db.session.add(User(username='Demo User', email='demo@gruha.com',
                            password_hash=generate_password_hash('demo123')))
    # Seed furniture catalog
    if Furniture.query.count() == 0:
        for name, cat, tags, price, img, desc in FURNITURE:
            db.session.add(Furniture(name=name, category=cat, style_tags=tags,
                                     price=price, image_url=img, description=desc))
    db.session.commit()
