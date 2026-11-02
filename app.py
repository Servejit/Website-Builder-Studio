import base64
import html
import json
import random
import re
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
    "theme-1": {"name": "Midnight Luxe", "bg": "#0c1018", "surface": "#151c28", "text": "#f7f4ed", "muted": "#aab3c2", "accent": "#d6b36a", "accent_text": "#17130b", "line": "#2c3544"},
    "theme-2": {"name": "Executive Blue", "bg": "#f4f7fb", "surface": "#ffffff", "text": "#14243a", "muted": "#63748a", "accent": "#2459a6", "accent_text": "#ffffff", "line": "#dce4ef"},
    "theme-3": {"name": "Modern Botanical", "bg": "#f4f5ed", "surface": "#ffffff", "text": "#1c332b", "muted": "#687c70", "accent": "#34745b", "accent_text": "#ffffff", "line": "#dce5dc"},
}


def clean(value):
    return html.escape(str(value or "").strip())


def slug(value):
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "brand"


def make_svg_placeholder(product, brand, number):
    title = html.escape(product[:28])
    brand_text = html.escape(brand[:30])
    palettes = [("#182333", "#d6b36a"), ("#e9eef5", "#2459a6"), ("#e9eee6", "#34745b")]
    bg, accent = palettes[(number - 1) % len(palettes)]
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 650">
    <defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{bg}"/><stop offset="1" stop-color="{accent}" stop-opacity=".28"/></linearGradient></defs>
    <rect width="900" height="650" fill="url(#g)"/>
    <circle cx="450" cy="275" r="145" fill="none" stroke="{accent}" stroke-width="3" opacity=".8"/>
    <circle cx="450" cy="275" r="115" fill="none" stroke="{accent}" stroke-width="1" opacity=".5"/>
    <path d="M450 165 L450 275 L520 315" fill="none" stroke="{accent}" stroke-width="7" stroke-linecap="round"/>
    <text x="450" y="500" text-anchor="middle" font-family="Arial" font-size="46" fill="{accent}">{title}</text>
    <text x="450" y="550" text-anchor="middle" font-family="Arial" font-size="22" fill="{accent}" opacity=".8">{brand_text} · PRODUCT VISUAL</text>
    </svg>"""
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


def image_to_data_url(upload):
    raw = upload.getvalue()
    mime = upload.type or "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(raw).decode('ascii')}"


def build_copy(product, brand, company):
    p = product.strip()
    b = brand.strip()
    key = p.lower()
    data = next((v for k, v in CATEGORY_CONTENT.items() if k in key), None)
    if data is None:
        data = DEFAULT_CONTENT
        importance = data["importance"].format(product_lc=p.lower())
    else:
        importance = data["importance"]
    company_name = company.strip() or b
    return {
        "company": company_name,
        "tagline": f"Thoughtfully chosen. Made for what matters.",
        "hero": f"Make every moment count with {b}.",
        "subhero": f"Discover {p} that brings purpose, personality and thoughtful design into your everyday life.",
        "importance": importance,
        "benefits": data["benefits"],
        "fit": data["fit"],
        "reasons": data["reasons"],
        "care": data["care"],
    }


def make_html(product, brand, company, email, phone, address, whatsapp, instagram, facebook, images):
    p, b = clean(product), clean(brand)
    c = build_copy(product, brand, company)
    gallery = "".join(
        f'<figure class="gallery-card"><img src="{src}" alt="{p} product photograph {i+1}" loading="lazy"><figcaption>{p} · View {i+1}</figcaption></figure>'
        for i, src in enumerate(images)
    )
    benefit_cards = "".join(f'<article class="info-card"><span class="number">0{i+1}</span><h3>{clean(x)}</h3><p>Thoughtfully considered for your everyday needs.</p></article>' for i, x in enumerate(c["benefits"]))
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
    # The form uses the visitor's email application. A real inbox submission service
    # can be connected later without changing the generated page layout.
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{clean(c['subhero'])}">
<meta name="theme-color" content="#0c1018">
<title>{b} | {p}</title>
<style>
:root{{--bg:#0c1018;--surface:#151c28;--text:#f7f4ed;--muted:#aab3c2;--accent:#d6b36a;--accentText:#17130b;--line:#2c3544;--shadow:0 22px 70px rgba(0,0,0,.12)}}
*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}body{{margin:0;background:var(--bg);color:var(--text);font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.65}}a{{color:inherit;text-decoration:none}}.wrap{{width:min(1160px,calc(100% - 42px));margin:auto}}.topbar{{position:sticky;top:0;z-index:10;background:color-mix(in srgb,var(--bg) 90%,transparent);backdrop-filter:blur(14px);border-bottom:1px solid var(--line)}}nav{{min-height:76px;display:flex;align-items:center;justify-content:space-between;gap:22px}}.logo{{font-weight:850;letter-spacing:.08em;font-size:20px}}.logo span{{color:var(--accent)}}.navlinks{{display:flex;gap:22px;align-items:center;font-size:13px;color:var(--muted)}}.navlinks a:hover{{color:var(--accent)}}.button{{display:inline-flex;align-items:center;justify-content:center;padding:13px 21px;border-radius:999px;background:var(--accent);color:var(--accentText);font-weight:750;font-size:13px;border:1px solid var(--accent);transition:.2s}}.button:hover{{transform:translateY(-2px);filter:brightness(1.08)}}.button-outline{{background:transparent;color:var(--text);border-color:var(--line)}}.hero{{padding:100px 0 85px;display:grid;grid-template-columns:1.05fr .95fr;gap:55px;align-items:center}}.eyebrow{{text-transform:uppercase;letter-spacing:.2em;font-size:11px;font-weight:800;color:var(--accent)}}h1{{font-size:clamp(42px,6vw,76px);line-height:1.04;letter-spacing:-.055em;margin:20px 0}}h2{{font-size:clamp(30px,4vw,48px);line-height:1.12;letter-spacing:-.04em;margin:12px 0 18px}}h3{{line-height:1.25}}.lead{{font-size:18px;color:var(--muted);max-width:590px}}.hero-actions{{display:flex;gap:12px;flex-wrap:wrap;margin-top:30px}}.hero-image{{min-height:420px;border-radius:28px;overflow:hidden;background:var(--surface);border:1px solid var(--line);box-shadow:var(--shadow)}}.hero-image img{{width:100%;height:100%;min-height:420px;object-fit:cover;display:block}}section{{padding:88px 0;border-top:1px solid var(--line)}}.section-head{{max-width:720px;margin-bottom:38px}}.section-head p,.body-copy{{color:var(--muted);font-size:16px}}.split{{display:grid;grid-template-columns:1fr 1fr;gap:55px;align-items:center}}.quote-panel{{padding:35px;border:1px solid var(--line);border-radius:24px;background:var(--surface);font-size:clamp(22px,3vw,32px);line-height:1.3}}.cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}}.info-card{{padding:25px;border:1px solid var(--line);border-radius:20px;background:var(--surface)}}.number{{font-size:12px;color:var(--accent);font-weight:800;letter-spacing:.15em}}.info-card h3{{font-size:18px}}.info-card p{{font-size:13px;color:var(--muted)}}.gallery{{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}}.gallery-card{{margin:0;border-radius:20px;overflow:hidden;border:1px solid var(--line);background:var(--surface)}}.gallery-card img{{display:block;width:100%;height:280px;object-fit:cover}}.gallery-card figcaption{{padding:14px 16px;color:var(--muted);font-size:13px}}.fit-panel{{padding:34px;border-radius:24px;background:var(--surface);border:1px solid var(--line)}}.reasons{{padding-left:22px;color:var(--muted)}}.reasons li{{padding:8px 0}}.faq details{{padding:18px 0;border-bottom:1px solid var(--line)}}.faq summary{{cursor:pointer;font-weight:700}}.faq p{{color:var(--muted)}}.contact-grid{{display:grid;grid-template-columns:.85fr 1.15fr;gap:35px}}.contact-panel{{background:var(--surface);border:1px solid var(--line);border-radius:24px;padding:28px}}.contact-panel a{{color:var(--accent);overflow-wrap:anywhere}}label{{display:block;font-size:12px;font-weight:700;margin:12px 0 6px}}input,textarea{{width:100%;padding:13px 14px;border:1px solid var(--line);border-radius:12px;background:var(--bg);color:var(--text);font:inherit}}textarea{{min-height:125px;resize:vertical}}.form-note{{font-size:12px;color:var(--muted)}}footer{{padding:38px 0;border-top:1px solid var(--line);color:var(--muted);font-size:13px}}.footer-inner{{display:flex;justify-content:space-between;gap:20px;flex-wrap:wrap}}.footer-links{{display:flex;gap:16px;flex-wrap:wrap}}.theme-label{{position:fixed;right:14px;bottom:14px;background:var(--surface);border:1px solid var(--line);color:var(--muted);padding:8px 12px;border-radius:99px;font-size:11px;z-index:20;opacity:.8}}
/* Three distinct page compositions */
body.design-luxe .hero{grid-template-columns:1fr 1fr;gap:28px;padding-top:72px}
body.design-luxe .hero-image{border-radius:4px 90px 4px 90px;min-height:510px}
body.design-luxe .hero-image img{min-height:510px}
body.design-luxe .topbar{border-bottom:2px solid var(--accent)}
body.design-luxe .logo{letter-spacing:.18em;text-transform:uppercase}
body.design-luxe .info-card,body.design-luxe .gallery-card{border-radius:4px 24px 4px 24px}
body.design-blue .hero{grid-template-columns:.9fr 1.1fr;padding:70px 0 95px}
body.design-blue .hero-image{order:2;border-radius:34px;box-shadow:0 25px 65px rgba(36,89,166,.18)}
body.design-blue .button{border-radius:12px}
body.design-blue .info-card{border-radius:14px;box-shadow:0 12px 32px rgba(20,36,58,.07)}
body.design-blue section{border-top:0}
body.design-blue .section-head{border-left:5px solid var(--accent);padding-left:20px}
body.design-botanical .hero{display:flex;flex-direction:column;text-align:center;gap:34px;padding:82px 0 76px}
body.design-botanical .hero>div:first-child{max-width:820px}
body.design-botanical .hero .lead{margin-left:auto;margin-right:auto}
body.design-botanical .hero-actions{justify-content:center}
body.design-botanical .hero-image{width:100%;max-width:900px;min-height:380px;border-radius:180px 180px 28px 28px}
body.design-botanical .hero-image img{min-height:380px}
body.design-botanical .button{border-radius:12px 28px 12px 28px}
body.design-botanical .info-card,body.design-botanical .gallery-card{border-radius:28px 8px 28px 8px}
body.design-botanical .quote-panel,body.design-botanical .fit-panel{border-radius:48px 12px 48px 12px}
@media(max-width:850px){body.design-luxe .hero,body.design-blue .hero{grid-template-columns:1fr}body.design-blue .hero-image{order:0}body.design-botanical .hero-image{min-height:280px;border-radius:100px 100px 20px 20px}body.design-botanical .hero-image img{min-height:280px}}
@media(max-width:850px){{.hero,.split,.contact-grid{{grid-template-columns:1fr}}.hero{{padding:65px 0}}.hero-image,.hero-image img{{min-height:310px}}.cards{{grid-template-columns:repeat(2,1fr)}}.gallery{{grid-template-columns:repeat(2,1fr)}}.navlinks{{display:none}}}}
@media(max-width:520px){{.wrap{{width:min(100% - 28px,1160px)}}section{{padding:62px 0}}.cards,.gallery{{grid-template-columns:1fr}}.gallery-card img{{height:250px}}.hero-actions .button{{width:100%}}}}
</style></head>
<body>
<header class="topbar"><div class="wrap"><nav><a class="logo" href="#home">{b}<span>.</span></a><div class="navlinks"><a href="#story">Our Story</a><a href="#benefits">Benefits</a><a href="#gallery">Gallery</a><a href="#faq">FAQ</a><a href="#contact">Contact</a></div><a class="button" href="#contact">Make an Enquiry</a></nav></div></header>
<main>
<div class="wrap hero" id="home"><div><div class="eyebrow">{clean(c['tagline'])}</div><h1>{clean(c['hero'])}</h1><p class="lead">{clean(c['subhero'])}</p><div class="hero-actions"><a class="button" href="#gallery">Explore {p}</a><a class="button button-outline" href="#contact">Talk to our team</a></div></div><div class="hero-image"><img src="{images[0]}" alt="{p} by {b}"></div></div>
<section id="story"><div class="wrap split"><div><div class="eyebrow">More than a product</div><h2>Why {p} matters in everyday life</h2><p class="body-copy">{clean(c['importance'])}</p><p class="body-copy">At {b}, our purpose is to help you make a considered choice that feels relevant to your life, your priorities and your personal style.</p></div><div class="quote-panel">“The best choices are the ones that make everyday moments feel more meaningful.”<p class="eyebrow">The {b} point of view</p></div></div></section>
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
(function(){{
 const themes={{
 "theme-1":{{bg:"#0c1018",surface:"#151c28",text:"#f7f4ed",muted:"#aab3c2",accent:"#d6b36a",accentText:"#17130b",line:"#2c3544",name:"Midnight Luxe",design:"design-luxe"}},
 "theme-2":{{bg:"#f4f7fb",surface:"#ffffff",text:"#14243a",muted:"#63748a",accent:"#2459a6",accentText:"#ffffff",line:"#dce4ef",name:"Executive Blue",design:"design-blue"}},
 "theme-3":{{bg:"#f4f5ed",surface:"#ffffff",text:"#1c332b",muted:"#687c70",accent:"#34745b",accentText:"#ffffff",line:"#dce5dc",name:"Modern Botanical",design:"design-botanical"}}
 }};
 const keys=Object.keys(themes);let previous=null;
 try{{previous=localStorage.getItem("website-builder-theme")||sessionStorage.getItem("website-builder-theme");}}catch(e){{}}
 let choices=keys.filter(k=>k!==previous);if(!choices.length)choices=keys;
 const selected=choices[Math.floor(Math.random()*choices.length)],t=themes[selected],root=document.documentElement;
 for(const [key,value] of Object.entries({{bg:t.bg,surface:t.surface,text:t.text,muted:t.muted,accent:t.accent,accentText:t.accentText,line:t.line}}))root.style.setProperty("--"+key,value);
 document.body.classList.remove("design-luxe","design-blue","design-botanical");document.body.classList.add(t.design);
 try{{localStorage.setItem("website-builder-theme",selected);sessionStorage.setItem("website-builder-theme",selected);}}catch(e){{}}
 const label=document.getElementById("theme-label");if(label)label.textContent="Design: "+t.name;
}})();
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
st.markdown('<p class="hero-sub">Two names in. A complete product and brand website out.</p>', unsafe_allow_html=True)
st.caption("Local content engine • Three responsive themes • Standalone HTML export • No paid API required")

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
    uploads = st.file_uploader("Upload 3–5 product images", type=["png", "jpg", "jpeg", "webp"], accept_multiple_files=True, help="Images are embedded into the downloaded HTML so the page can work offline.")
    st.caption("If you do not upload images, the builder inserts designed visual placeholders. Upload real product photos before publishing.")

if "generated_html" not in st.session_state:
    st.session_state.generated_html = ""
if "generated_key" not in st.session_state:
    st.session_state.generated_key = ""

left, right = st.columns([1.05, .95], gap="large")
with left:
    st.markdown("### Build your website")
    st.markdown('<div class="panel"><b>Only two required fields</b><p class="small-muted">Product tells the builder what you sell. Brand tells it how to present your business. Company and contact details are optional and editable.</p></div>', unsafe_allow_html=True)
    st.write("")
    st.markdown("**Your website will include**")
    features = ["Hero banner and brand message", "Product importance and lifestyle story", "Benefits, reasons to buy and customer fit", "3–5 image gallery", "About company and FAQ", "Contact details and consumer enquiry form", "Privacy and terms starter sections", "Mobile responsive layout and SEO metadata", "Three colour themes that rotate on refresh"]
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
        st.session_state.generated_html = make_html(product, brand, company, email, phone, address, whatsapp, instagram, facebook, selected_images)
        st.session_state.generated_key = f"{product.strip()}|{brand.strip()}"
        st.success("Your website has been generated. Preview it and download the HTML below.")
    if not can_build:
        st.caption("Enter both names and upload no more than five images to generate.")

with right:
    st.markdown("### What gets generated")
    st.markdown('<div class="panel"><div style="font-size:2rem;font-weight:800;color:#f4f7fb">Your brand. Your story.</div><p class="small-muted">A polished, responsive product website with a consistent message and a rotating visual identity.</p><div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:14px"><span style="padding:7px 12px;border-radius:99px;background:#d6b36a;color:#17130b">Midnight Luxe</span><span style="padding:7px 12px;border-radius:99px;background:#dce8f8;color:#14243a">Executive Blue</span><span style="padding:7px 12px;border-radius:99px;background:#dce9df;color:#1c332b">Botanical</span></div></div>', unsafe_allow_html=True)
    st.write("")
    st.info("The page content stays the same across refreshes. Only its colour theme changes. The downloaded HTML includes all three themes and chooses one when opened.")

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
    st.caption("The HTML contains embedded uploaded images and all three themes. It does not require Streamlit to run. The contact form uses the visitor's email app; for automatic form delivery, connect a form backend.")
    if st.button("Clear generated website and start again"):
        st.session_state.generated_html = ""
        st.session_state.generated_key = ""
        st.rerun()

st.divider()
st.markdown("### Important before publishing")
st.warning("This builder creates persuasive starter copy locally; it does not verify product claims, prices, certifications, stock, company history or legal compliance. Replace placeholders with accurate business information. A working enquiry inbox requires an email recipient and the visitor's email application, or a separately configured form service.")
st.caption("Website Builder Studio · Built with Streamlit · No paid AI API")
