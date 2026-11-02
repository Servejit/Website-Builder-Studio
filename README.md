# Website Builder Studio

A Streamlit app that turns a product name and brand name into a responsive, standalone HTML product website.

## Features

- Required inputs: product name and brand name.
- Optional company name, email, phone, WhatsApp, address and social links.
- Upload 3–5 product images; images are embedded in the downloaded HTML.
- If no image is uploaded, designed placeholders are added to the gallery.
- Automatically generated product story, benefits, customer fit, buying reasons, FAQ, contact and legal starter sections.
- Three themes: Midnight Luxe, Executive Blue and Modern Botanical. The exported page randomly changes theme on each page load while keeping its content and images unchanged.
- Download as one standalone HTML file.
- No paid AI API or API key required.

## Run locally

Python 3.10 or newer is recommended.

    pip install -r requirements.txt
    streamlit run app.py

## Deploy with Streamlit Community Cloud

1. Open https://share.streamlit.io/
2. Sign in with GitHub.
3. Select Servejit/Website-Builder-Studio.
4. Select branch main and file app.py.
5. Deploy.

## Important notes

The current content engine uses local category-aware templates and does not call an AI service. It can generate useful starter copy without API keys, but it does not verify product specifications, prices, certifications, company history or legal claims. Review all generated content before publishing.

The exported HTML is self-contained when product images are uploaded. The enquiry form uses the visitor's default email application (mailto:); it does not store or automatically deliver submissions on its own. To receive enquiries reliably without requiring the visitor's email app, connect a form backend or your own server-side email endpoint.

The privacy and terms sections are starter text, not legal advice. Replace them with policies suitable for the business and jurisdiction.
