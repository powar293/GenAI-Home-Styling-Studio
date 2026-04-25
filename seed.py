"""Seed the database with furniture items and a demo user."""
from app import app
from models import db, User, Furniture
from werkzeug.security import generate_password_hash

FURNITURE = [
    # Modern
    ("L-Shaped Sofa", "Seating", "modern,scandinavian", 45000, "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400", "Sleek sectional with clean lines"),
    ("Glass Coffee Table", "Tables", "modern", 12000, "https://images.unsplash.com/photo-1549187774-b4e9b0445b41?w=400", "Tempered glass with chrome frame"),
    ("LED Floor Lamp", "Lighting", "modern,minimal", 5500, "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=400", "Minimalist arc floor lamp"),
    ("Floating TV Unit", "Storage", "modern,minimal", 18000, "https://images.unsplash.com/photo-1598928636135-d146006ff4be?w=400", "Wall-mounted media console"),
    ("Ergonomic Chair", "Seating", "modern,industrial", 22000, "https://images.unsplash.com/photo-1580480055273-228ff5388ef8?w=400", "Mesh-back office chair"),
    # Classic
    ("Chesterfield Sofa", "Seating", "classic", 65000, "https://images.unsplash.com/photo-1506439773649-6e0eb8cfb237?w=400", "Button-tufted leather sofa"),
    ("Crystal Chandelier", "Lighting", "classic", 28000, "https://images.unsplash.com/photo-1565814329452-e1efa11c5b89?w=400", "6-arm crystal chandelier"),
    ("Wingback Chair", "Seating", "classic,bohemian", 18000, "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400", "Velvet wingback accent chair"),
    # Minimal
    ("Platform Bed", "Bedroom", "minimal,scandinavian", 28000, "https://images.unsplash.com/photo-1505693314120-0d443867891c?w=400", "Low-profile walnut bed frame"),
    ("Linen Sofa", "Seating", "minimal,scandinavian", 32000, "https://images.unsplash.com/photo-1493663284031-b7e3aefcae8e?w=400", "Natural linen 3-seater"),
    ("Drum Pendant Light", "Lighting", "minimal,scandinavian", 7500, "https://images.unsplash.com/photo-1513506003901-1e6a35f5b3d4?w=400", "Linen drum shade pendant"),
    # Bohemian
    ("Rattan Sofa", "Seating", "bohemian", 24000, "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400", "Natural rattan with cushions"),
    ("Moroccan Pouf", "Seating", "bohemian", 5000, "https://images.unsplash.com/photo-1594938291221-94f18cbb5660?w=400", "Embroidered leather pouf"),
    ("Hanging Planter Set", "Decor", "bohemian,scandinavian", 2500, "https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=400", "Boho rope plant hangers"),
    # Industrial
    ("Metal Pipe Shelf", "Storage", "industrial", 9500, "https://images.unsplash.com/photo-1532372320978-9b4f355c8e5c?w=400", "Black iron pipe with wood boards"),
    ("Leather Sofa", "Seating", "industrial,classic", 55000, "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400", "Distressed brown leather 3-seater"),
    ("Edison Pendant", "Lighting", "industrial", 3500, "https://images.unsplash.com/photo-1515890435782-59a5bb6ec191?w=400", "Exposed filament pendant bulb"),
    ("Factory Bar Stool", "Seating", "industrial", 4500, "https://images.unsplash.com/photo-1551298370-9d3d53740c72?w=400", "Adjustable metal bar stool"),
    # Scandinavian
    ("Hygge Armchair", "Seating", "scandinavian,minimal", 19000, "https://images.unsplash.com/photo-1567538096621-38d2284b23ff?w=400", "Cosy bouclé accent chair"),
    ("Birch Dining Table", "Tables", "scandinavian", 27000, "https://images.unsplash.com/photo-1530018607912-eff2daa1bac4?w=400", "Light birch with tapered legs"),
]

def seed():
    with app.app_context():
        db.create_all()
        # Demo user
        if not User.query.filter_by(email='demo@gruha.com').first():
            db.session.add(User(username='Demo User', email='demo@gruha.com',
                                password_hash=generate_password_hash('demo123')))
        # Furniture
        if Furniture.query.count() == 0:
            for name, cat, tags, price, img, desc in FURNITURE:
                db.session.add(Furniture(name=name, category=cat, style_tags=tags,
                                         price=price, image_url=img, description=desc))
        db.session.commit()
        print("✅ Database seeded! Demo login: demo@gruha.com / demo123")

if __name__ == '__main__':
    seed()
