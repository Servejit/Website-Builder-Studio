import base64
import html
import json
import re
import random
from datetime import datetime
from io import BytesIO

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Website Builder Studio",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------------------------------------------------------
# Website content engine: local templates, no paid API or API key.
# -------------------------------------------------------------------
CATEGORY_CONTENT = {
    "watch": {
        "importance": "Time is one of the few things we can never recover. The right watch is more than a way to read the hour: it is a daily reminder to value your time, honour your commitments and make every moment count.",
        "benefits": ["A clear expression of personal style", "A useful companion for work and everyday occasions", "A thoughtful gift for meaningful milestones", "A daily reminder to stay punctual and purposeful"],
        "fit": "For people who value punctuality, personal presentation and making the most of every opportunity.",
        "reasons": ["Bring confidence to your everyday look", "Choose an accessory that works across occasions", "Celebrate time, progress and personal milestones"],
        "care": "Choose a style and fit that feels comfortable for your everyday routine. Review the actual product specifications and care instructions before purchase.",
    },
    "shoe": {
        "importance": "Every journey begins with a step. The right footwear supports your everyday movement, helps you feel prepared and brings comfort and confidence to the moments that matter.",
        "benefits": ["Designed to complement everyday outfits", "A practical choice for daily routines", "A balance of personal style and function", "A versatile addition to your wardrobe"],
        "fit": "For people who are always moving, exploring, working or making their next step count.",
        "reasons": ["Complete your look with confidence", "Choose footwear suited to your routine", "Make every step part of your personal style"],
        "care": "Check the size guide, materials and care instructions for the exact model before purchase.",
    },
    "phone": {
        "importance": "A phone connects people, ideas and opportunities. It can help you communicate, learn, create and stay organised throughout the day.",
        "benefits": ["A companion for communication and daily tasks", "Helps keep your digital life within reach", "Supports work, learning and entertainment", "A practical part of a connected lifestyle"],
        "fit": "For people who communicate, create, learn and manage everyday life on the move.",
        "reasons": ["Choose a device that fits your daily needs", "Keep important connections close", "Compare verified specifications before deciding"],
        "care": "Confirm the exact model, storage, warranty, network compatibility and specifications before purchase.",
    },
    "bag": {
        "importance": "The things you carry support the things you do. A well-chosen bag helps keep essentials organised while complementing your personal style.",
        "benefits": ["A practical way to organise daily essentials", "Complements work, travel and everyday outfits", "A useful choice for busy routines", "Combines personal expression with everyday utility"],
        "fit": "For students, professionals, travellers and anyone who likes to keep essentials organised.",
        "reasons": ["Make everyday organisation easier", "Choose a style that suits your routine", "Carry your essentials with confidence"],
        "care": "Check dimensions, capacity, material and care instructions to ensure the bag suits your needs.",
    },
    "perfume": {
        "importance": "A scent can become part of how a moment is remembered. Fragrance is a personal expression that can complement your mood, style and occasion.",
        "benefits": ["A personal finishing touch", "Can complement different occasions", "A thoughtful gifting option", "An expression of individual taste"],
        "fit": "For people who enjoy expressing their personality through thoughtful details and personal style.",
        "reasons": ["Explore a scent that feels like you", "Choose a fragrance for your preferred occasions", "Make gifting more personal"],
        "care": "Review fragrance notes, size, ingredients and usage guidance. Individual scent preferences vary.",
    },
    "clothing": {
        "importance": "What you wear can help you feel ready for the day. Clothing is a practical part of comfort, self-expression and the confidence to show up as yourself.",
        "benefits": ["A way to express your individual style", "Options for different routines and occasions", "A practical part of everyday confidence", "Easy to make your own with personal styling"],
        "fit": "For people who see clothing as a way to express their identity and feel comfortable in their day.",
        "reasons": ["Refresh your everyday wardrobe", "Choose pieces that fit your lifestyle", "Express your style with confidence"],
        "care": "Check the size chart, fabric composition, fit and washing instructions before purchase.",
    },
}
DEFAULT_CONTENT = {
    "importance": "The right {product_lc} can make a meaningful difference to everyday life. It should do more than serve a purpose: it should fit naturally into your routine, reflect your preferences and help you enjoy the moments that matter.",
    "benefits": ["A thoughtful addition to everyday life", "Designed to complement your personal preferences", "A practical option for different occasions", "A way to express your individual style"],
    "fit": "For people who value thoughtful choices, everyday usefulness and products that complement their lifestyle.",
    "reasons": ["Choose something that fits your needs", "Bring purpose and personality to your everyday routine", "Make a considered choice that feels right for you"],
    "care": "Review the exact product description, materials, dimensions, compatibility and care instructions before purchasing.",
}

THEMES = {
}

DESIGN_DIRECTIONS = [
    {"name":"Editorial / Heritage","style":"editorial","tagline":"A story worth discovering.","hero":"A more considered way to experience {product}.","subhero":"{brand} brings a thoughtful point of view to {product}, with character, detail and meaning.","story":"Every memorable brand begins with a point of view. {brand} sees {product} as more than an item to own: it is part of a personal ritual, a considered choice and a reflection of what matters to you.","quote":"Good design is what you feel, remember and return to.","label":"The art of thoughtful choice"},
    {"name":"Bold / Avant-Garde","style":"bold","tagline":"Made to make a statement.","hero":"{product}. Without the ordinary.","subhero":"Meet the {brand} perspective: confident, expressive and made for people who set the pace.","story":"The world does not need another ordinary choice. {brand} is for people who bring their own energy to every room, every plan and every possibility. {product} becomes an expression of that attitude.","quote":"Don't blend into the moment. Give it a point of view.","label":"A different kind of confidence"},
    {"name":"Organic / Human","style":"organic","tagline":"Thoughtfully made for real life.","hero":"Bring more meaning to every day.","subhero":"{brand} celebrates the everyday moments around {product}—the routines, connections and small details that make life your own.","story":"The best things fit naturally into real life. {brand} starts with people: what they value, how they spend their days and the little details that make a difference. That is the spirit behind our approach to {product}.","quote":"A meaningful everyday experience is built from thoughtful little details.","label":"Designed around real life"},
    {"name":"Luxury / Minimal","style":"luxury","tagline":"Less noise. More intention.","hero":"The quiet confidence of {product}.","subhero":"Discover the understated {brand} approach: clarity, considered details and a refined perspective on the things you choose.","story":"True refinement does not need to compete for attention. It is found in considered decisions, clear purpose and details that feel right. {brand} brings that quieter perspective to {product}.","quote":"When every detail has a purpose, simplicity becomes its own signature.","label":"The signature of simplicity"},
    {"name":"Future / Digital","style":"future","tagline":"A fresh perspective starts here.","hero":"Rethink what {product} can mean.","subhero":"{brand} looks at {product} through a fresh lens—where useful ideas, modern living and individual expression meet.","story":"New expectations create room for better experiences. {brand} is built around curiosity, practical thinking and the belief that the next chapter of {product} should feel relevant to the way people live now.","quote":"The future belongs to ideas that make a real difference today.","label":"A fresh point of view"},
]


def readable_text_color(hex_color):
    """Choose near-black or white text with strong contrast for a hex background."""
    value = hex_color.lstrip("#")
    if len(value) != 6:
        return "#172033"
    channels = [int(value[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    linear = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in channels]
    luminance = 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]
    return "#142033" if luminance > 0.42 else "#FFFFFF"


def make_palette(background, accent):
    text_color = readable_text_color(background)
    is_light = text_color != "#FFFFFF"
    return {
        "bg": background,
        "surface": "#FFFFFF" if is_light else "#172235",
        "text": text_color,
        "muted": "#526174" if is_light else "#C1CAD6",
        "accent": accent,
        "accent_text": readable_text_color(accent),
        "line": "#DCE3EB" if is_light else "#35445A",
    }

def clean(value):
    return html.escape(str(value or "").strip())


def slug(value):
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "brand"


def make_svg_placeholder(product, brand, number):
    title = html.escape(product[:30])
    brand_text = html.escape(brand[:32])
    backgrounds = [("#EAF0F6", "#315477"), ("#F1ECE5", "#8B6546"), ("#E9EFEA", "#456B58")]
    bg, accent = backgrounds[(number - 1) % len(backgrounds)]
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 650">
    <defs>
      <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{bg}"/><stop offset="1" stop-color="#FFFFFF"/></linearGradient>
      <linearGradient id="shape" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{accent}" stop-opacity=".92"/><stop offset="1" stop-color="{accent}" stop-opacity=".48"/></linearGradient>
    </defs>
    <rect width="900" height="650" fill="url(#bg)"/>
    <circle cx="720" cy="110" r="190" fill="{accent}" opacity=".07"/>
    <circle cx="160" cy="560" r="210" fill="{accent}" opacity=".06"/>
    <rect x="280" y="135" width="340" height="300" rx="34" fill="url(#shape)" opacity=".14"/>
    <path d="M330 390 L450 205 L570 390 Z" fill="url(#shape)" opacity=".82"/>
    <rect x="345" y="410" width="210" height="13" rx="7" fill="{accent}" opacity=".3"/>
    <text x="450" y="505" text-anchor="middle" font-family="Arial,sans-serif" font-size="42" font-weight="700" fill="{accent}">{title}</text>
    <text x="450" y="548" text-anchor="middle" font-family="Arial,sans-serif" font-size="20" letter-spacing="3" fill="{accent}" opacity=".8">{brand_text}</text>
    <text x="450" y="585" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" letter-spacing="4" fill="{accent}" opacity=".65">PRODUCT IMAGE PLACEHOLDER</text>
    </svg>"""
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()

def image_to_data_url(upload):
    raw = upload.getvalue()
    mime = upload.type or "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(raw).decode('ascii')}"


def detect_brand_personality(brand, product):
    """Infer a lightweight brand personality from words; entirely local and editable."""
    words = set(re.findall(r"[a-z]+", (brand + " " + product).lower()))
    profiles = [
        ("premium", {"luxury", "elite", "royal", "prestige", "gold", "signature", "prime", "imperial", "platinum"}),
        ("modern", {"tech", "digital", "neo", "nova", "future", "smart", "cyber", "next", "byte"}),
        ("natural", {"eco", "green", "earth", "organic", "nature", "pure", "flora", "root", "leaf"}),
        ("energetic", {"power", "sport", "active", "flash", "bold", "turbo", "rapid", "force", "max"}),
        ("creative", {"art", "studio", "craft", "design", "colour", "color", "urban", "unique", "creative"}),
        ("trustworthy", {"trust", "care", "safe", "honest", "true", "reliable", "secure", "classic"}),
    ]
    scores = [(name, len(words & cues)) for name, cues in profiles]
    best = max(scores, key=lambda item: item[1])
    if best[1] == 0:
        return random.choice(["confident", "thoughtful", "modern", "approachable"])
    return best[0]


def build_copy(product, brand, company, direction):
    """Create varied brand copy from local word signals and modular story patterns."""
    p, b = product.strip(), brand.strip()
    key = p.lower()
    data = next((v for k, v in CATEGORY_CONTENT.items() if k in key), None)
    if data is None:
        data = DEFAULT_CONTENT
        importance = data["importance"].format(product_lc=p.lower())
    else:
        importance = data["importance"]

    personality = detect_brand_personality(b, p)
    audience_by_category = {
        "watch": ["people who value personal style and punctuality", "professionals who appreciate considered details", "gift buyers marking an important moment"],
        "shoe": ["people who are always on the move", "style-conscious everyday explorers", "customers balancing comfort and personal expression"],
        "phone": ["connected creators and everyday problem-solvers", "people who work, learn and communicate on the move", "customers who compare practical technology choices"],
        "bag": ["busy professionals and students", "frequent travellers and organised planners", "people who want function with personal style"],
        "perfume": ["people who enjoy personal expression", "thoughtful gift-givers", "customers who choose details to match their mood"],
        "clothing": ["people who use style to express themselves", "customers building a versatile wardrobe", "anyone who values comfort and individuality"],
    }
    category = next((k for k in CATEGORY_CONTENT if k in key), "general")
    audiences = audience_by_category.get(category, [
        "people who appreciate useful, well-considered choices",
        "customers looking for products that fit their everyday lives",
        "people who value individuality and practical details",
    ])
    audience = random.choice(audiences)

    personality_language = {
        "premium": ("refined", "considered details and understated confidence", "quietly distinctive"),
        "modern": ("forward-looking", "fresh thinking and useful innovation", "ready for what comes next"),
        "natural": ("grounded", "a more thoughtful connection with everyday life", "closer to what matters"),
        "energetic": ("bold", "movement, confidence and expressive choices", "made to stand out"),
        "creative": ("expressive", "individuality, imagination and original points of view", "never just another choice"),
        "trustworthy": ("dependable", "clarity, care and confidence in the details", "a choice you can feel good about"),
        "confident": ("confident", "personality and purpose in everyday choices", "comfortable being different"),
        "thoughtful": ("thoughtful", "small details that make an everyday difference", "made with intention"),
        "modern": ("modern", "fresh ideas for the way people live now", "in step with today"),
        "approachable": ("approachable", "useful choices and a welcoming experience", "easy to make your own"),
    }
    adjective, values, signature = personality_language[personality]

    story_openers = [
        "{brand} began with a simple question: what should a better {product} experience feel like?",
        "A product becomes meaningful when it fits into a real person's life. That belief shapes {brand}.",
        "Everyday choices say something about us. {brand} brings a distinct point of view to {product}.",
        "The idea behind {brand} is simple: make the experience of choosing {product} feel more considered.",
        "There is always room to rethink the familiar. That is where the {brand} approach to {product} begins.",
        "Behind every considered choice is a reason. For {brand}, that reason starts with people and their everyday needs.",
    ]
    story_middle = [
        "Our perspective is shaped by {values}. We want {audience} to find an option that feels relevant, useful and personal.",
        "We focus on {values}, with an experience intended for {audience}. The aim is not to follow every trend, but to make a choice feel right.",
        "For {audience}, the details matter. Our approach brings together {values} and a clear sense of individual style.",
        "That means thinking beyond the product itself: how it is discovered, how it fits a routine and what makes it memorable for {audience}.",
        "We believe good choices should feel natural. By focusing on {values}, {brand} gives {audience} a fresh way to look at {product}.",
    ]
    story_endings = [
        "That is the standard we want the {brand} name to represent: {signature}.",
        "The result is a brand point of view that feels {adjective}, personal and grounded in real life.",
        "Because the best choice is not simply noticed; it is the one that continues to feel right.",
        "For us, {product} is the starting point. A better everyday experience is the bigger idea.",
        "This is {brand}: a distinct perspective, built around the details people care about.",
    ]
    headlines = [
        "A fresh point of view on {product}.",
        "{product}, seen differently.",
        "Make room for a more {adjective} choice.",
        "The details make the difference.",
        "Find your own way with {product}.",
        "A better feeling starts with the right choice.",
        "Bring a new perspective to the everyday.",
        "Not just another {product}. Your kind of choice.",
    ]
    taglines = [
        "A different point of view. The {brand} way.",
        "Made for the way you choose.",
        "More character in every detail.",
        "Find what feels right.",
        "Thoughtful choices. Distinctive living.",
        "Your everyday, with a little more meaning.",
        "A fresh take on the familiar.",
        "Choose with confidence. Live with character.",
    ]
    subheroes = [
        "{brand} brings a {adjective} perspective to {product}, shaped by {values}.",
        "Discover {product} through the {brand} approach: {values}, personality and a focus on real life.",
        "For {audience}, {brand} makes space for a more personal way to think about {product}.",
        "A considered approach to {product}, created for people who want their choices to mean something.",
        "Explore a distinctive take on {product}, where everyday usefulness meets individual expression.",
    ]
    quotes = [
        "A good choice should feel right long after the first impression.",
        "Distinctive is not about being louder. It is about knowing what matters.",
        "The smallest details can shape the whole experience.",
        "Make the everyday feel a little more your own.",
        "A point of view is what turns a product into a brand.",
        "Choose with purpose. Make it personal.",
        "The best ideas begin by looking at familiar things differently.",
    ]

    values_text = values
    fmt = {
        "brand": b, "product": p, "audience": audience, "values": values_text,
        "adjective": adjective, "signature": signature,
    }
    story = " ".join([
        random.choice(story_openers).format(**fmt),
        random.choice(story_middle).format(**fmt),
        random.choice(story_endings).format(**fmt),
    ])
    hero = random.choice(headlines).format(**fmt)
    subhero = random.choice(subheroes).format(**fmt)
    tagline = random.choice(taglines).format(**fmt)
    quote = random.choice(quotes)
    return {
        "company": company.strip() or b,
        "tagline": tagline,
        "hero": hero,
        "subhero": subhero,
        "brand_story": story,
        "quote": quote,
        "story_label": random.choice(["The thinking behind the brand", "A point of view with purpose", "The {brand} philosophy".format(**fmt), "More than the product", "Where our story begins"]),
        "design_name": direction["name"],
        "design_style": direction["style"],
        "importance": importance,
        "benefits": data["benefits"],
        "fit": data["fit"],
        "reasons": data["reasons"],
        "care": data["care"],
    }


def make_html(product, brand, company, email, phone, address, whatsapp, instagram, facebook, images, background_color, accent_color, direction):
    p, b = clean(product), clean(brand)
    c = build_copy(product, brand, company, direction)
    gallery = "".join(
        f'<figure class="gallery-card"><img src="{src}" alt="{p} product photograph {i+1}" loading="lazy"><figcaption>{p} · View {i+1}</figcaption></figure>'
        for i, src in enumerate(images)
    )
    benefit_descriptions = [
        "A practical point of value to consider when comparing your options.",
        "A detail that can make the product more useful in your daily routine.",
        "An option to match your personal preferences and intended use.",
        "A reason to explore the product and decide whether it suits your needs.",
    ]
    benefit_cards = "".join(
        f'<article class="info-card"><span class="number">0{i+1}</span><h3>{clean(x)}</h3><p>{clean(benefit_descriptions[i % len(benefit_descriptions)])}</p></article>'
        for i, x in enumerate(c["benefits"])
    )
    reasons = "".join(f"<li>{clean(x)}</li>" for x in c["reasons"])
    email_link = f"mailto:{clean(email)}" if email.strip() else "#contact"
    phone_link = "tel:" + re.sub(r"[^0-9+]", "", phone) if phone.strip() else "#contact"
    wa_number = re.sub(r"\D", "", whatsapp)
    wa_link = f"https://wa.me/{wa_number}" if wa_number else ""
    social = ""
    if instagram.strip():
        social += f'<a href="{clean(instagram)}" target="_blank" rel="noopener">Instagram</a>'
    if facebook.strip():
        social += f'<a href="{clean(facebook)}" target="_blank" rel="noopener">Facebook</a>'
    contact_lines = []
    if email.strip(): contact_lines.append(f'<a href="{email_link}">{clean(email)}</a>')
    if phone.strip(): contact_lines.append(f'<a href="{phone_link}">{clean(phone)}</a>')
    if address.strip(): contact_lines.append(f'<span>{clean(address)}</span>')
    contact_html = "".join(f"<p>{x}</p>" for x in contact_lines) or "<p>Company contact details will be added here.</p>"
    wa_button = f'<a class="button button-outline" href="{wa_link}" target="_blank" rel="noopener">Chat on WhatsApp</a>' if wa_link else ""
    safe_company = c["company"]
    year = datetime.now().year
    palette = make_palette(background_color, accent_color)
    # The form uses the visitor's email application. A real inbox submission service
    # can be connected later without changing the generated page layout.
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{clean(c['subhero'])}">
<meta name="theme-color" content="{palette["bg"]}">
<title>{b} | {p}</title>
<style>
:root{{--bg:{palette["bg"]};--surface:{palette["surface"]};--text:{palette["text"]};--muted:{palette["muted"]};--accent:{palette["accent"]};--accentText:{palette["accent_text"]};--line:{palette["line"]};--shadow:0 24px 70px rgba(18,32,51,.10);--radius:22px}}
*{{box-sizing:border-box}}
html{{scroll-behavior:smooth;scroll-padding-top:95px}}
body{{margin:0;background:var(--bg);color:var(--text);font-family:Inter,"Segoe UI",Arial,sans-serif;line-height:1.7;-webkit-font-smoothing:antialiased}}
a{{color:inherit;text-decoration:none}}
.wrap{{width:min(1160px,calc(100% - 48px));margin:0 auto}}
.topbar{{position:sticky;top:0;z-index:20;background:var(--surface);border-bottom:1px solid var(--line);box-shadow:0 4px 18px rgba(18,32,51,.04)}}
nav{{min-height:78px;display:flex;align-items:center;justify-content:space-between;gap:24px}}
.logo{{font-size:22px;font-weight:850;letter-spacing:-.04em;color:var(--text)}}
.logo span{{color:var(--accent)}}
.navlinks{{display:flex;gap:26px;align-items:center;color:var(--muted);font-size:13px;font-weight:650}}
.navlinks a:hover{{color:var(--accent)}}
.button{{display:inline-flex;align-items:center;justify-content:center;min-height:48px;padding:12px 22px;border-radius:10px;background:var(--accent);color:var(--accentText);font-size:13px;font-weight:800;border:1px solid var(--accent);transition:transform .18s,box-shadow .18s}}
.button:hover{{transform:translateY(-2px);box-shadow:0 10px 24px rgba(18,32,51,.14)}}
.button-outline{{background:transparent;color:var(--text);border-color:var(--line)}}
.hero{{padding:82px 0 86px;display:grid;grid-template-columns:1fr 1fr;gap:64px;align-items:center}}
.eyebrow{{color:var(--accent);font-size:11px;font-weight:850;letter-spacing:.16em;text-transform:uppercase}}
h1{{font-size:clamp(42px,5.4vw,68px);line-height:1.07;letter-spacing:-.055em;margin:18px 0 22px;max-width:680px}}
h2{{font-size:clamp(30px,3.7vw,46px);line-height:1.14;letter-spacing:-.04em;margin:12px 0 18px}}
h3{{line-height:1.3;margin:12px 0}}
.lead{{font-size:18px;line-height:1.75;color:var(--muted);max-width:570px}}
.hero-actions{{display:flex;gap:12px;flex-wrap:wrap;margin-top:30px}}
.hero-image{{height:480px;overflow:hidden;border-radius:var(--radius);background:var(--surface);border:1px solid var(--line);box-shadow:var(--shadow)}}
.hero-image img{{width:100%;height:100%;object-fit:cover;display:block}}
section{{padding:82px 0;border-top:1px solid var(--line)}}
.section-head{{max-width:720px;margin-bottom:36px}}
.section-head p,.body-copy{{color:var(--muted);font-size:16px;line-height:1.8}}
.split{{display:grid;grid-template-columns:1fr 1fr;gap:54px;align-items:center}}
.quote-panel,.fit-panel{{padding:34px;border:1px solid var(--line);border-radius:var(--radius);background:var(--surface);box-shadow:var(--shadow)}}
.quote-panel{{font-size:clamp(22px,2.7vw,30px);line-height:1.4;font-weight:650}}
.cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:18px}}
.info-card{{padding:26px 24px;border:1px solid var(--line);border-radius:16px;background:var(--surface);box-shadow:0 8px 26px rgba(18,32,51,.045)}}
.number{{color:var(--accent);font-size:12px;font-weight:900;letter-spacing:.14em}}
.info-card h3{{font-size:17px}}
.info-card p{{color:var(--muted);font-size:13px;line-height:1.7}}
.gallery{{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}}
.gallery-card{{margin:0;overflow:hidden;border:1px solid var(--line);border-radius:16px;background:var(--surface)}}
.gallery-card img{{display:block;width:100%;height:290px;object-fit:cover}}
.gallery-card figcaption{{padding:14px 17px;color:var(--muted);font-size:13px;font-weight:650}}
.reasons{{padding-left:22px;color:var(--muted)}}
.reasons li{{padding:8px 0}}
.faq details{{padding:19px 0;border-bottom:1px solid var(--line)}}
.faq summary{{cursor:pointer;font-weight:750;color:var(--text)}}
.faq p{{color:var(--muted)}}
.contact-grid{{display:grid;grid-template-columns:.85fr 1.15fr;gap:24px}}
.contact-panel{{padding:28px;border:1px solid var(--line);border-radius:var(--radius);background:var(--surface)}}
.contact-panel a{{color:var(--accent);overflow-wrap:anywhere}}
label{{display:block;margin:13px 0 6px;font-size:12px;font-weight:750}}
input,textarea{{width:100%;padding:13px 14px;border:1px solid var(--line);border-radius:10px;background:var(--bg);color:var(--text);font:inherit;outline:none}}
input:focus,textarea:focus{{border-color:var(--accent);box-shadow:0 0 0 3px color-mix(in srgb,var(--accent) 16%,transparent)}}
textarea{{min-height:125px;resize:vertical}}
.form-note{{color:var(--muted);font-size:12px;line-height:1.65}}
footer{{padding:34px 0;border-top:1px solid var(--line);color:var(--muted);font-size:13px;background:var(--surface)}}
.footer-inner{{display:flex;justify-content:space-between;gap:20px;flex-wrap:wrap}}
.footer-links{{display:flex;gap:18px;flex-wrap:wrap}}
@media(max-width:900px){{.hero{{gap:34px}}.cards{{grid-template-columns:repeat(2,1fr)}}.navlinks{{gap:14px}}}}
@media(max-width:700px){{.wrap{{width:calc(100% - 32px)}}nav{{min-height:68px}}.navlinks{{display:none}}.hero,.split,.contact-grid{{grid-template-columns:1fr}}.hero{{padding:56px 0 62px;gap:30px}}.hero-image{{height:340px}}section{{padding:62px 0}}.gallery{{grid-template-columns:1fr 1fr}}.gallery-card img{{height:230px}}.hero-actions .button{{flex:1}}}}
@media(max-width:460px){{.cards,.gallery{{grid-template-columns:1fr}}.gallery-card img{{height:260px}}.hero-actions{{flex-direction:column}}.hero-actions .button{{width:100%}}}}
/* Distinct creative systems: every generation changes more than the colour palette. */
body[data-design="editorial"] .hero{{padding-top:105px;gap:7vw}} body[data-design="editorial"] h1,body[data-design="editorial"] h2{{font-family:Georgia,serif;font-weight:500;letter-spacing:-.045em}} body[data-design="editorial"] .hero-image{{border-radius:2px 110px 2px 2px}} body[data-design="editorial"] .info-card{{border-radius:2px;box-shadow:none}}
body[data-design="bold"] h1{{font-size:clamp(52px,7vw,92px);font-weight:950;letter-spacing:-.075em;text-transform:uppercase;line-height:.94}} body[data-design="bold"] .hero-image{{border-radius:4px;transform:rotate(1.5deg);box-shadow:18px 18px 0 var(--accent)}} body[data-design="bold"] .button{{border-radius:2px;text-transform:uppercase;letter-spacing:.08em}} body[data-design="bold"] .info-card{{border-radius:4px;border-top:5px solid var(--accent)}}
body[data-design="organic"] h1,body[data-design="organic"] h2{{font-family:Georgia,serif;font-weight:500}} body[data-design="organic"] .hero-image{{border-radius:48% 48% 18px 18px}} body[data-design="organic"] .quote-panel,body[data-design="organic"] .fit-panel{{border-radius:42px 12px 42px 12px}} body[data-design="organic"] .info-card{{border-radius:26px 8px 26px 8px}}
body[data-design="luxury"] .hero{{padding-top:125px;padding-bottom:115px}} body[data-design="luxury"] h1{{font-family:Georgia,serif;font-weight:400;letter-spacing:-.055em}} body[data-design="luxury"] .hero-image{{border-radius:0;box-shadow:none}} body[data-design="luxury"] .info-card,body[data-design="luxury"] .quote-panel,body[data-design="luxury"] .fit-panel{{border-radius:0;box-shadow:none}} body[data-design="luxury"] .button{{border-radius:0;letter-spacing:.1em;text-transform:uppercase;font-size:11px}}
body[data-design="future"] .hero-image{{border-radius:28px;box-shadow:0 0 0 1px var(--accent),0 24px 70px rgba(18,32,51,.16)}} body[data-design="future"] .info-card{{border-radius:20px;background:linear-gradient(145deg,var(--surface),var(--bg))}} body[data-design="future"] .button{{border-radius:999px}} body[data-design="future"] .quote-panel,body[data-design="future"] .fit-panel{{border-radius:28px}}
@media(max-width:700px){{body[data-design] .hero{{grid-template-columns:1fr;padding-top:55px}}body[data-design="bold"] h1{{font-size:clamp(44px,13vw,68px)}}body[data-design="bold"] .hero-image{{transform:none}}}}
</style></head>
<body data-design="{c['design_style']}">
<header class="topbar"><div class="wrap"><nav><a class="logo" href="#home">{b}<span>.</span></a><div class="navlinks"><a href="#story">Our Story</a><a href="#benefits">Benefits</a><a href="#gallery">Gallery</a><a href="#faq">FAQ</a><a href="#contact">Contact</a></div><a class="button" href="#contact">Make an Enquiry</a></nav></div></header>
<main>
<div class="wrap hero" id="home"><div><div class="eyebrow">{clean(c['tagline'])}</div><h1>{clean(c['hero'])}</h1><p class="lead">{clean(c['subhero'])}</p><div class="hero-actions"><a class="button" href="#gallery">Explore {p}</a><a class="button button-outline" href="#contact">Talk to our team</a></div></div><div class="hero-image"><img src="{images[0]}" alt="{p} by {b}"></div></div>
<section id="story"><div class="wrap split"><div><div class="eyebrow">{clean(c['story_label'])}</div><h2>The idea behind {b}</h2><p class="body-copy">{clean(c['brand_story'])}</p><p class="body-copy">{clean(c['importance'])}</p></div><div class="quote-panel">“{clean(c['quote'])}”<p class="eyebrow">{b} · {clean(c['design_name'])}</p></div></div></section>
<section id="benefits"><div class="wrap"><div class="section-head"><div class="eyebrow">The {b} difference</div><h2>Thoughtful reasons to choose {b}</h2><p>Explore the everyday value and practical benefits to consider when choosing your {p.lower()}.</p></div><div class="cards">{benefit_cards}</div></div></section>
<section id="gallery"><div class="wrap"><div class="section-head"><div class="eyebrow">A closer look</div><h2>The {p} gallery</h2><p>Product photographs supplied for this brand presentation. Confirm the exact product, colour and model before ordering.</p></div><div class="gallery">{gallery}</div></div></section>
<section id="you"><div class="wrap split"><div class="fit-panel"><div class="eyebrow">Made to fit your life</div><h2>How {p} suits you</h2><p class="body-copy">{clean(c['fit'])}</p></div><div><div class="eyebrow">A considered decision</div><h2>Why consider buying from {b}?</h2><ul class="reasons">{reasons}</ul><p class="body-copy">{clean(c['care'])}</p><a class="button" href="#contact">Ask us before you buy</a></div></div></section>
<section id="about"><div class="wrap"><div class="section-head"><div class="eyebrow">About the company</div><h2>Meet {clean(safe_company)}</h2><p class="body-copy">{b} is presented as a brand focused on making the {p.lower()} choice feel clear, relevant and considered. We believe a good customer experience begins with useful information, honest details and helpful communication.</p><p class="form-note">This is an editable starter brand story. Replace it with your verified company history, mission, location and credentials before publishing.</p></div></div></section>
<section id="faq"><div class="wrap"><div class="section-head"><div class="eyebrow">Helpful information</div><h2>Frequently asked questions</h2></div><div class="faq">
<details><summary>How do I choose the right {p.lower()}?</summary><p>Consider your needs, preferred style, intended use and budget. Contact the {b} team if you need help reviewing product details.</p></details>
<details><summary>Where can I find product specifications?</summary><p>Ask the company for the verified specifications, available variants, dimensions, materials, warranty and current price before ordering.</p></details>
<details><summary>How can I make a purchase enquiry?</summary><p>Use the enquiry form below or contact the company through the details provided on this page.</p></details>
<details><summary>What are your delivery, return and warranty terms?</summary><p>Please request the current written delivery, return, refund and warranty policies from the company before purchase. Terms vary by product and seller.</p></details>
</div></div></section>
<section id="contact"><div class="wrap"><div class="section-head"><div class="eyebrow">We are here to help</div><h2>Contact {b}</h2><p>Have a question about {p.lower()}? Send a consumer enquiry and the company can get back to you.</p></div><div class="contact-grid"><div class="contact-panel"><h3>{clean(safe_company)}</h3>{contact_html}{social}{wa_button}<p class="form-note">Add verified company contact information in the builder before publishing.</p></div><div class="contact-panel"><form id="enquiry"><label for="name">Your name</label><input id="name" name="name" required placeholder="Enter your name"><label for="visitor-email">Email address</label><input id="visitor-email" name="email" type="email" required placeholder="you@example.com"><label for="visitor-phone">Phone (optional)</label><input id="visitor-phone" name="phone" placeholder="Your phone number"><label for="subject">Enquiry subject</label><input id="subject" name="subject" value="Enquiry about {p}"><label for="message">Your message</label><textarea id="message" name="message" required placeholder="How can we help you?"></textarea><button class="button" type="submit">Prepare enquiry email</button><p class="form-note">This standalone page opens your email application with the enquiry prepared. It does not transmit or store submissions by itself. Configure a form backend to receive enquiries automatically.</p><p id="form-status" class="form-note" aria-live="polite"></p></form></div></div></div></section>
<section id="legal"><div class="wrap"><div class="section-head"><div class="eyebrow">Customer information</div><h2>Privacy & terms</h2><p class="body-copy"><strong>Privacy:</strong> This static website does not itself store enquiry form submissions. If you connect analytics, a mailing list or a form provider, update this notice to explain what data is collected, why it is collected, how long it is retained and how customers can contact you about their data.</p><p class="body-copy"><strong>Terms:</strong> Product descriptions, prices, availability, delivery, returns, warranties and other purchase conditions must be confirmed by the seller and displayed accurately before a transaction. This generated page is a starter template, not legal advice. Replace this section with terms reviewed for your business and location.</p></div></div></section>
</main>
<footer><div class="wrap footer-inner"><div><strong>{b}</strong> · © {year} {clean(safe_company)}. All rights reserved.</div><div class="footer-links"><a href="#about">About</a><a href="#contact">Contact</a><a href="#legal">Privacy & Terms</a></div></div></footer>
<div class="theme-label" id="theme-label">Theme</div>
<script>
document.getElementById("enquiry").addEventListener("submit",function(e){{
 e.preventDefault();
 const form=new FormData(this);
 const to={json.dumps(email.strip())};
 if(!to){{document.getElementById("form-status").textContent="The company has not added a receiving email address yet. Please use the contact details shown on this page.";return;}}
 const subject=encodeURIComponent(form.get("subject")||"Website enquiry");
 const body=encodeURIComponent("Name: "+form.get("name")+"\nEmail: "+form.get("email")+"\nPhone: "+form.get("phone")+"\n\n"+form.get("message"));
 window.location.href="mailto:"+to+"?subject="+subject+"&body="+body;
 document.getElementById("form-status").textContent="Your email application should open with the enquiry details.";
}});
</script></body></html>"""


# -------------------------------------------------------------------
# Streamlit dashboard
# -------------------------------------------------------------------
st.markdown("""
<style>
.stApp{background:linear-gradient(145deg,#0b1220 0%,#101b2c 55%,#101827 100%)}
.block-container{max-width:1450px;padding-top:2rem;padding-bottom:3rem}
[data-testid="stSidebar"]{background:#101827}
.hero-title{font-size:clamp(2rem,5vw,3.6rem);font-weight:850;letter-spacing:-.05em;color:#f4f7fb;line-height:1.08}
.hero-sub{color:#aebbd0;font-size:1.05rem}
.panel{background:rgba(255,255,255,.045);border:1px solid rgba(255,255,255,.10);border-radius:18px;padding:18px}
.small-muted{color:#aebbd0;font-size:.88rem}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero-title">Website Builder Studio ✦</div>', unsafe_allow_html=True)
st.markdown('<p class="hero-sub">Two words in. A fresh brand identity, story and website direction every time.</p>', unsafe_allow_html=True)
st.caption("Professional responsive design • Custom brand colours • Standalone HTML export • No paid API required")

with st.sidebar:
    st.markdown("## ✦ Studio")
    st.markdown("### 1 · Brand essentials")
    product = st.text_input("Product name", value="Watch", placeholder="e.g. Watch")
    brand = st.text_input("Brand name", value="TimeServe", placeholder="e.g. TimeServe")
    company = st.text_input("Company name (optional)", placeholder="Defaults to brand name")
    st.markdown("---")
    st.markdown("### 2 · Contact details (optional)")
    email = st.text_input("Business email", placeholder="hello@example.com")
    phone = st.text_input("Business phone", placeholder="+91 ...")
    whatsapp = st.text_input("WhatsApp number", placeholder="Country code + number, digits only")
    address = st.text_area("Business address", placeholder="Add your verified business address")
    instagram = st.text_input("Instagram profile URL", placeholder="https://instagram.com/...")
    facebook = st.text_input("Facebook page URL", placeholder="https://facebook.com/...")
    st.markdown("---")
    st.markdown("### 3 · Product photographs")
    st.markdown("### 4 · Website colours")
    background_color = st.color_picker("Website background", "#F5F7FA", help="Text and card colours are selected automatically for readability.")
    accent_color = st.color_picker("Brand accent colour", "#173B66", help="Used for buttons, links and highlights.")
    uploads = st.file_uploader("Upload 3–5 product images", type=["png", "jpg", "jpeg", "webp"], accept_multiple_files=True, help="Images are embedded into the downloaded HTML so the page can work offline.")
    st.caption("If you do not upload images, the builder inserts designed visual placeholders. Upload real product photos before publishing.")

if "generated_html" not in st.session_state:
    st.session_state.generated_html = ""
if "generated_key" not in st.session_state:
    st.session_state.generated_key = ""
if "generation_count" not in st.session_state:
    st.session_state.generation_count = 0

left, right = st.columns([1.05, .95], gap="large")
with left:
    st.markdown("### Build your website")
    st.markdown('<div class="panel"><b>Only two required fields</b><p class="small-muted">Product tells the builder what you sell. Brand tells it how to present your business. Company and contact details are optional and editable.</p></div>', unsafe_allow_html=True)
    st.write("")
    st.markdown("**Your website will include**")
    features = ["Hero banner and brand message", "Product importance and lifestyle story", "Benefits, reasons to buy and customer fit", "3–5 image gallery", "About company and FAQ", "Contact details and consumer enquiry form", "Privacy and terms starter sections", "Mobile responsive layout and SEO metadata", "A rotating creative direction: editorial, bold, organic, luxury or future-inspired"]
    for item in features:
        st.markdown(f"✓ {item}")
    if len(uploads or []) > 5:
        st.warning("Please upload no more than 5 images.")
    if uploads and len(uploads) < 3:
        st.info("You uploaded fewer than 3 images. You can still generate the page; placeholders will fill the gallery.")
    can_build = bool(product.strip() and brand.strip() and len(uploads or []) <= 5)
    if st.button("✦ Generate complete website", type="primary", use_container_width=True, disabled=not can_build):
        selected_images = [image_to_data_url(f) for f in (uploads or [])]
        while len(selected_images) < 3:
            selected_images.append(make_svg_placeholder(product, brand, len(selected_images) + 1))
        selected_images = selected_images[:5]
        direction = DESIGN_DIRECTIONS[st.session_state.generation_count % len(DESIGN_DIRECTIONS)]
        st.session_state.generation_count += 1
        st.session_state.generated_html = make_html(product, brand, company, email, phone, address, whatsapp, instagram, facebook, selected_images, background_color, accent_color, direction)
        st.session_state.generated_key = f"{product.strip()}|{brand.strip()} · {direction['name']}"
        st.success(f"Fresh creative direction generated: {direction['name']}. Generate again for a different impression.")
    if not can_build:
        st.caption("Enter both names and upload no more than five images to generate.")

with right:
    st.markdown("### What gets generated")
    st.markdown('<div class="panel"><div style="font-size:2rem;font-weight:800;color:#f4f7fb">Your brand. Your story.</div><p class="small-muted">One polished, consistent layout. Choose your own background and brand accent colours; text contrast is calculated automatically.</p></div>', unsafe_allow_html=True)
    st.write("")
    st.info("Every generation rotates through five distinct design directions. Story angle, typography, shapes, spacing and layout treatment change while your chosen colours and uploaded images are retained.")

if st.session_state.generated_html:
    st.divider()
    st.markdown("## Website preview")
    st.caption(f"Generated for {st.session_state.generated_key.replace('|', ' · ')}")
    components.html(st.session_state.generated_html, height=900, scrolling=True)
    st.download_button(
        "⬇ Download complete standalone website (.html)",
        data=st.session_state.generated_html.encode("utf-8"),
        file_name=f"{slug(brand)}-{slug(product)}-website.html",
        mime="text/html",
        type="primary",
        use_container_width=True,
    )
    st.caption("The HTML contains embedded uploaded images and your selected colour scheme. It does not require Streamlit to run. The contact form uses the visitor's email app; for automatic form delivery, connect a form backend.")
    if st.button("Clear generated website and start again"):
        st.session_state.generated_html = ""
        st.session_state.generated_key = ""
        st.rerun()

st.divider()
st.markdown("### Important before publishing")
st.warning("This builder creates persuasive starter copy locally; it does not verify product claims, prices, certifications, stock, company history or legal compliance. Replace placeholders with accurate business information. A working enquiry inbox requires an email recipient and the visitor's email application, or a separately configured form service.")
st.caption("Website Builder Studio · Built with Streamlit · No paid AI API")
