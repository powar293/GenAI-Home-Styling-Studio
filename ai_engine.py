import google.generativeai as genai
import json, os, urllib.parse
from PIL import Image
from config import Config

genai.configure(api_key=Config.GEMINI_API_KEY)

# ── Budget ranges (label → min, max in INR) ──────────────────────────────────
BUDGET_RANGES = {
    "25k-50k":  (25000,  50000),
    "50k-1l":   (50000,  100000),
    "1l-2l":    (100000, 200000),
    "2l-5l":    (200000, 500000),
    "5l+":      (500000, 1500000),
}

ROOM_TYPES = [
    "Living Room", "Bedroom", "Kitchen",
    "Bathroom", "Office", "Dining Room",
]

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


# ── Room Validation ──────────────────────────────────────────────────────────

def validate_room_image(image_path: str) -> dict:
    """Use Gemini Vision to verify the uploaded image is an interior room.
    Returns {"is_room": bool, "message": str}.
    """
    prompt = (
        "Look at this image carefully. Is this an image of an interior room or indoor space "
        "(like a living room, bedroom, kitchen, bathroom, office, dining room, etc.)?\n\n"
        "Return ONLY valid JSON (no extra text) with this exact structure:\n"
        '{"is_room": true, "room_type": "Living Room", "message": "Valid room detected."}\n'
        "OR if it is NOT a room:\n"
        '{"is_room": false, "room_type": null, "message": "This does not appear to be an interior room. '
        'Please upload a clear photo of a room interior."}\n'
    )
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        img = Image.open(image_path)
        response = model.generate_content([prompt, img])
        return _parse_json(response.text)
    except Exception as exc:
        print(f"[ai_engine] validate_room_image error: {exc}")
        # On failure, allow through (don't block the user)
        return {"is_room": True, "room_type": "Room", "message": "Validation skipped."}


# ── Room Analysis (budget-aware) ─────────────────────────────────────────────

def analyze_room(image_path: str | None, style: str,
                 room_type: str = "Living Room",
                 budget_key: str = "1l-2l") -> dict:
    """Call Gemini Vision to analyse the room with budget constraints.
    The AI must keep total furniture cost within the user's budget range.
    Falls back to mock data (filtered by budget) on error.
    """
    style_key = style.lower()
    budget_min, budget_max = BUDGET_RANGES.get(budget_key, (100000, 200000))

    prompt = (
        f"You are an expert Indian interior designer. Analyse this room image and give recommendations "
        f"for a **{style}** style **{room_type}**.\n\n"
        f"**IMPORTANT BUDGET CONSTRAINT**: The customer's total budget is ₹{budget_min:,} to ₹{budget_max:,}.\n"
        f"- The TOTAL COST of ALL furniture items MUST be within this budget range.\n"
        f"- If budget is low (under ₹50,000), suggest only 2-3 essential items.\n"
        f"- If budget is moderate (₹50,000–₹2,00,000), suggest 4-5 items.\n"
        f"- If budget is high (above ₹2,00,000), suggest 5-7 premium items.\n"
        f"- Each item's individual price must be realistic in INR for the Indian market.\n"
        f"- Look closely at the structural layout of the uploaded room (e.g. 'large window on the left, wood floor, sloped ceiling'). Describe this structural layout in 15-20 words in the 'room_layout' field.\n\n"
        "Return ONLY valid JSON (no extra text) with this exact structure:\n"
        '{"furniture":[{"name":"...","category":"Seating|Tables|Lighting|Storage|Decor|Bedroom","price":0,"style":"...","desc":"..."}],'
        '"colors":[{"name":"...","hex":"#xxxxxx","role":"Primary|Secondary|Accent|Background"}],'
        '"tips":["..."],"room_type":"...","estimated_budget":"₹X,XX,XXX","room_layout":"..."}\n\n'
        f"Prices in INR. Total of all furniture prices MUST be between ₹{budget_min:,} and ₹{budget_max:,}.\n"
        f"Include 4 colours and 4 design tips."
    )
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        if image_path and os.path.exists(image_path):
            img = Image.open(image_path)
            response = model.generate_content([prompt, img])
        else:
            response = model.generate_content(
                prompt + f"\n(No image provided – generate for a typical {style} {room_type}.)"
            )
        suggestions = _parse_json(response.text)

        # Attach generated room visualization URL
        room_layout = suggestions.get('room_layout', '')
        suggestions['visual_suggestion_url'] = _build_visual_url(
            style, room_type, suggestions.get('furniture', []), room_layout
        )
        return suggestions

    except Exception as exc:
        print(f"[ai_engine] analyze_room error: {exc}")
        data = MOCK.get(style_key, MOCK["modern"]).copy()
        data["room_type"] = room_type

        # Filter mock furniture to fit within budget
        data["furniture"] = _filter_furniture_by_budget(
            data["furniture"], budget_min, budget_max
        )
        total = sum(f["price"] for f in data["furniture"])
        data["estimated_budget"] = f"₹{total:,}"

        data['visual_suggestion_url'] = _build_visual_url(
            style, room_type, data["furniture"], ""
        )
        return data


def _filter_furniture_by_budget(furniture_list: list, budget_min: int, budget_max: int) -> list:
    """Filter/trim mock furniture list so total cost fits within budget."""
    # Sort by price ascending, accumulate until we hit budget max
    sorted_items = sorted(furniture_list, key=lambda f: f["price"])
    selected = []
    running_total = 0
    for item in sorted_items:
        if running_total + item["price"] <= budget_max:
            selected.append(item)
            running_total += item["price"]
    # Ensure at least 1 item
    if not selected and sorted_items:
        selected = [sorted_items[0]]
    return selected


def _build_visual_url(style: str, room_type: str, furniture_list: list, room_layout: str = "") -> str:
    """Build a Pollinations AI image URL for the furnished room visualization."""
    style_keywords = {
        'modern': 'sleek, glass, contemporary, minimalist',
        'classic': 'elegant, traditional, ornate wood',
        'minimal': 'clean, simple, spacious, white',
        'bohemian': 'colorful, plants, eclectic, textiles',
        'industrial': 'raw, metal, exposed brick, concrete',
        'scandinavian': 'light wood, cozy, hygge, neutral tones'
    }
    keywords = style_keywords.get(style.lower(), 'modern')
    furniture_names = ", ".join(f["name"] for f in furniture_list[:4])
    
    layout_str = f" The room structure must match this layout exactly: {room_layout}." if room_layout else ""

    img_prompt = (
        f"Professional interior design photo of a beautiful {style.capitalize()} style {room_type}.{layout_str} "
        f"It is furnished with {furniture_names}, {keywords}, "
        f"warm lighting, photorealistic, 8k, highly detailed, interior magazine quality"
    )
    encoded = urllib.parse.quote(img_prompt)
    return f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=720&nologo=true"


# ── Buddy Chat ───────────────────────────────────────────────────────────────

def buddy_chat(message: str, lang: str, user_id: int, design_id=None) -> dict:
    """Run AI Buddy conversation via Gemini; return structured response."""
    lang_name = {"en": "English", "hi": "Hindi", "mr": "Marathi"}.get(lang, "English")

    context_str = "You are Buddy, the expert AI interior design assistant for Gruha Alankara."
    if design_id:
        try:
            from models import Design
            design = Design.query.get(design_id)
            if design:
                context_str += f"\nContext: User is currently working on a {design.style} style design."
        except Exception:
            pass

    prompt = (
        f"{context_str}\n"
        f"You are Buddy Voice, an expert AI interior designer.\n"
        f"You help users design rooms based on room dimensions, budget, style preference, and furniture needs.\n"
        f"Always:\n"
        f"- Ask follow-up questions if information is missing.\n"
        f"- Suggest furniture with realistic estimated costs in INR.\n"
        f"- Recommend matching colors and lighting.\n"
        f"- Keep responses friendly and conversational.\n"
        f"Always reply fluently and naturally in {lang_name}.\n"
        f"User said: \"{message}\"\n\n"
        "Analyze the user's request and reply with ONLY this valid JSON (no markdown formatting or extra text):\n"
        "{\n"
        '  "response": "<your conversational spoken reply in the requested language>",\n'
        '  "intent": "suggest|book|chat",\n'
        '  "furniture_name": "<name if booking intent else null>",\n'
        '  "furniture_suggestions": [\n'
        '    {"name": "L-shaped sofa", "price": 35000, "material": "Fabric", "image_url": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=400&q=80"}\n'
        '  ],\n'
        '  "estimated_budget": {\n'
        '    "items": [\n'
        '       {"item": "L-shaped sofa", "cost": 35000}\n'
        '    ],\n'
        '    "total": 35000\n'
        '  },\n'
        '  "colors": ["#1a1a3e", "#f0f4f8"]\n'
        "}\n"
        "If booking intent, accurately extract the furniture item name the user wants to book.\n"
        "For furniture image_url, provide a relevant placeholder Unsplash image URL (e.g. for a sofa, bed, etc.)."
    )
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        return _parse_json(response.text)
    except Exception as exc:
        print(f"[ai_engine] buddy_chat error: {exc}")
        error_msg = str(exc)
        if "429" in error_msg or "quota" in error_msg.lower():
            fallback_text = "I am receiving too many requests right now and my Google API quota is exceeded. Please wait a minute and try again!"
        else:
            fallback_text = BUDDY_FALLBACK.get(lang, BUDDY_FALLBACK["en"])
            
        return {
            "response": fallback_text,
            "intent": "chat",
            "furniture_name": None,
            "furniture_suggestions": [],
            "estimated_budget": {"items": [], "total": 0},
            "colors": []
        }
