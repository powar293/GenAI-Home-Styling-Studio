import google.generativeai as genai
import json, os
from PIL import Image
from config import Config

genai.configure(api_key=Config.GEMINI_API_KEY)

# ── Mock fallback data ────────────────────────────────────────────────────────
MOCK = {
    "modern": {
        "furniture": [
            {"name": "L-Shaped Sofa", "category": "Seating", "price": 45000, "style": "modern", "desc": "Sleek sectional with clean lines"},
            {"name": "Glass Coffee Table", "category": "Tables", "price": 12000, "style": "modern", "desc": "Tempered glass with chrome frame"},
            {"name": "LED Floor Lamp", "category": "Lighting", "price": 5500, "style": "modern", "desc": "Minimalist arc floor lamp"},
            {"name": "Floating TV Unit", "category": "Storage", "price": 18000, "style": "modern", "desc": "Wall-mounted media console"},
            {"name": "Ergonomic Chair", "category": "Seating", "price": 22000, "style": "modern", "desc": "Mesh-back office chair"},
        ],
        "colors": [
            {"name": "Midnight Navy", "hex": "#1a1a3e", "role": "Primary"},
            {"name": "Arctic White", "hex": "#f0f4f8", "role": "Secondary"},
            {"name": "Electric Teal", "hex": "#00d4aa", "role": "Accent"},
            {"name": "Charcoal", "hex": "#2d3436", "role": "Background"},
        ],
        "tips": [
            "Use low-profile furniture to maximize visual space",
            "Add geometric rugs for texture contrast",
            "Install LED strips for ambient under-cabinet lighting",
            "Use large mirrors to reflect natural light",
        ],
        "room_type": "Living Room",
        "estimated_budget": "₹1,02,500",
    },
    "classic": {
        "furniture": [
            {"name": "Chesterfield Sofa", "category": "Seating", "price": 65000, "style": "classic", "desc": "Button-tufted leather sofa"},
            {"name": "Wooden Dining Table", "category": "Tables", "price": 35000, "style": "classic", "desc": "Solid teak with carved legs"},
            {"name": "Crystal Chandelier", "category": "Lighting", "price": 28000, "style": "classic", "desc": "6-arm crystal chandelier"},
            {"name": "Bookshelf Cabinet", "category": "Storage", "price": 22000, "style": "classic", "desc": "Mahogany with glass doors"},
            {"name": "Wingback Chair", "category": "Seating", "price": 18000, "style": "classic", "desc": "Velvet wingback accent chair"},
        ],
        "colors": [
            {"name": "Walnut Brown", "hex": "#5c3317", "role": "Primary"},
            {"name": "Ivory Cream", "hex": "#fffff0", "role": "Secondary"},
            {"name": "Royal Gold", "hex": "#ffd700", "role": "Accent"},
            {"name": "Forest Green", "hex": "#228b22", "role": "Background"},
        ],
        "tips": [
            "Layer rugs over hardwood floors for warmth",
            "Mix textures: velvet, wood, and metal",
            "Add crown moulding for an elegant finish",
            "Use warm white bulbs for a cozy ambience",
        ],
        "room_type": "Dining Room",
        "estimated_budget": "₹1,68,000",
    },
    "minimal": {
        "furniture": [
            {"name": "Platform Bed", "category": "Bedroom", "price": 28000, "style": "minimal", "desc": "Low-profile walnut bed frame"},
            {"name": "Floating Shelves", "category": "Storage", "price": 6000, "style": "minimal", "desc": "Pine wood wall shelves"},
            {"name": "Pendant Light", "category": "Lighting", "price": 4500, "style": "minimal", "desc": "Concrete-finish pendant"},
            {"name": "Linen Sofa", "category": "Seating", "price": 32000, "style": "minimal", "desc": "Natural linen 3-seater"},
            {"name": "Side Table", "category": "Tables", "price": 4000, "style": "minimal", "desc": "Bamboo round side table"},
        ],
        "colors": [
            {"name": "Off White", "hex": "#fafaf8", "role": "Primary"},
            {"name": "Warm Sand", "hex": "#d4b896", "role": "Secondary"},
            {"name": "Stone Grey", "hex": "#9e9e9e", "role": "Accent"},
            {"name": "Natural Oak", "hex": "#c8a882", "role": "Background"},
        ],
        "tips": [
            "Keep surfaces clear and clutter-free",
            "Choose furniture with hidden storage",
            "Stick to a 3-color palette maximum",
            "Let natural light be your primary light source",
        ],
        "room_type": "Bedroom",
        "estimated_budget": "₹74,500",
    },
    "bohemian": {
        "furniture": [
            {"name": "Rattan Sofa", "category": "Seating", "price": 24000, "style": "bohemian", "desc": "Natural rattan with cushions"},
            {"name": "Macramé Wall Art", "category": "Decor", "price": 3500, "style": "bohemian", "desc": "Hand-woven macramé panel"},
            {"name": "Moroccan Pouf", "category": "Seating", "price": 5000, "style": "bohemian", "desc": "Embroidered leather pouf"},
            {"name": "Hanging Planter", "category": "Decor", "price": 2500, "style": "bohemian", "desc": "Boho rope plant hanger"},
            {"name": "Low Floor Table", "category": "Tables", "price": 8000, "style": "bohemian", "desc": "Reclaimed wood coffee table"},
        ],
        "colors": [
            {"name": "Terracotta", "hex": "#c4613a", "role": "Primary"},
            {"name": "Sage Green", "hex": "#87a96b", "role": "Secondary"},
            {"name": "Saffron", "hex": "#f4a62a", "role": "Accent"},
            {"name": "Dusty Rose", "hex": "#dcb4a0", "role": "Background"},
        ],
        "tips": [
            "Layer colourful textiles and throw pillows",
            "Mix patterns: geometric, floral, and tribal",
            "Use plants liberally for a jungle feel",
            "Hang fairy lights for a warm glow",
        ],
        "room_type": "Living Room",
        "estimated_budget": "₹43,000",
    },
    "industrial": {
        "furniture": [
            {"name": "Metal Pipe Shelf", "category": "Storage", "price": 9500, "style": "industrial", "desc": "Black iron pipe with wood boards"},
            {"name": "Leather Sofa", "category": "Seating", "price": 55000, "style": "industrial", "desc": "Distressed brown leather 3-seater"},
            {"name": "Edison Bulb Pendant", "category": "Lighting", "price": 3500, "style": "industrial", "desc": "Exposed filament pendant"},
            {"name": "Factory Stool", "category": "Seating", "price": 4500, "style": "industrial", "desc": "Adjustable metal bar stool"},
            {"name": "Reclaimed Wood Table", "category": "Tables", "price": 22000, "style": "industrial", "desc": "Solid wood with metal legs"},
        ],
        "colors": [
            {"name": "Raw Steel", "hex": "#708090", "role": "Primary"},
            {"name": "Exposed Brick", "hex": "#b5651d", "role": "Secondary"},
            {"name": "Rusty Orange", "hex": "#cc5500", "role": "Accent"},
            {"name": "Carbon Black", "hex": "#1c1c1c", "role": "Background"},
        ],
        "tips": [
            "Expose brick walls or use brick wallpaper",
            "Mix metal and wood for an authentic feel",
            "Keep window treatments minimal",
            "Add vintage maps or blueprint art",
        ],
        "room_type": "Studio",
        "estimated_budget": "₹94,500",
    },
    "scandinavian": {
        "furniture": [
            {"name": "Hygge Armchair", "category": "Seating", "price": 19000, "style": "scandinavian", "desc": "Cosy bouclé accent chair"},
            {"name": "Birch Dining Table", "category": "Tables", "price": 27000, "style": "scandinavian", "desc": "Light birch with tapered legs"},
            {"name": "Drum Pendant Light", "category": "Lighting", "price": 7500, "style": "scandinavian", "desc": "White linen drum shade"},
            {"name": "Modular Bookcase", "category": "Storage", "price": 14000, "style": "scandinavian", "desc": "Stackable pine modules"},
            {"name": "Sheepskin Rug", "category": "Decor", "price": 6500, "style": "scandinavian", "desc": "Genuine sheepskin throw"},
        ],
        "colors": [
            {"name": "Nordic White", "hex": "#f9f9f6", "role": "Primary"},
            {"name": "Pale Blue", "hex": "#b0c4de", "role": "Secondary"},
            {"name": "Dusty Teal", "hex": "#5f9ea0", "role": "Accent"},
            {"name": "Light Pine", "hex": "#d4a96a", "role": "Background"},
        ],
        "tips": [
            "Maximise natural light with sheer curtains",
            "Use candles for hygge warmth in evenings",
            "Keep colour palette light and neutral",
            "Add a wool throw for texture and comfort",
        ],
        "room_type": "Living Room",
        "estimated_budget": "₹74,000",
    },
}

BUDDY_FALLBACK = {
    "en": "I'm Buddy, your AI design assistant! I can suggest furniture, help you book items, or answer any design question. What would you like?",
    "hi": "मैं बडी हूँ, आपका AI डिज़ाइन सहायक! मैं फर्नीचर सुझा सकता हूँ, बुकिंग में मदद कर सकता हूँ। आप क्या चाहते हैं?",
    "mr": "मी बडी आहे, तुमचा AI डिझाईन सहाय्यक! मी फर्निचर सुचवू शकतो, बुकिंग करू शकतो. तुम्हाला काय हवे आहे?",
}


def _parse_json(text: str) -> dict:
    """Extract JSON from Gemini response which may wrap it in markdown fences."""
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]
    return json.loads(text.strip())


def analyze_room(image_path: str | None, style: str) -> dict:
    """Call Gemini Vision to analyse the room; fall back to mock on error."""
    style_key = style.lower()
    prompt = (
        f"You are an expert interior designer. Analyse this room image and give recommendations "
        f"for a **{style}** style interior. "
        "Return ONLY valid JSON (no extra text) with this exact structure:\n"
        '{"furniture":[{"name":"...","category":"...","price":0,"style":"...","desc":"..."}],'
        '"colors":[{"name":"...","hex":"#xxxxxx","role":"Primary|Secondary|Accent|Background"}],'
        '"tips":["..."],"room_type":"...","estimated_budget":"₹X,XX,XXX"}\n'
        "Include 5 furniture items (prices in INR), 4 colours, 4 tips."
    )
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        if image_path and os.path.exists(image_path):
            img = Image.open(image_path)
            response = model.generate_content([prompt, img])
        else:
            response = model.generate_content(
                prompt + f"\n(No image provided – generate for a typical {style} room.)"
            )
        return _parse_json(response.text)
    except Exception as exc:
        print(f"[ai_engine] analyze_room error: {exc}")
        return MOCK.get(style_key, MOCK["modern"])


def buddy_chat(message: str, lang: str, user_id: int, design_id=None) -> dict:
    """Run AI Buddy conversation via Gemini; return structured response."""
    lang_name = {"en": "English", "hi": "Hindi", "mr": "Marathi"}.get(lang, "English")
    prompt = (
        f"You are Buddy, the AI interior design assistant for Gruha Alankara.\n"
        f"Always reply in {lang_name}.\n"
        f"User said: \"{message}\"\n\n"
        "Detect intent and reply with ONLY this JSON:\n"
        '{"response":"<reply in language>","intent":"suggest|book|view_bookings|chat",'
        '"furniture_name":"<name if booking else null>","suggestions":["item1","item2"]}\n'
        "If booking intent, extract the furniture item name the user wants to book."
    )
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return _parse_json(response.text)
    except Exception as exc:
        print(f"[ai_engine] buddy_chat error: {exc}")
        return {
            "response": BUDDY_FALLBACK.get(lang, BUDDY_FALLBACK["en"]),
            "intent": "chat",
            "furniture_name": None,
            "suggestions": [],
        }
