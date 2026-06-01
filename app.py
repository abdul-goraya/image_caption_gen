import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import re
import io
import time

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Product Caption Generator",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)
# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main { background-color: #f8f9fc; }

    .hero-banner {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem 2rem;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(102,126,234,0.3);
    }
    .hero-banner h1 { font-size: 2.4rem; font-weight: 700; margin: 0; }
    .hero-banner p  { font-size: 1.05rem; opacity: 0.9; margin-top: 0.5rem; }

    .result-card {
        background: white;
        border-radius: 14px;
        padding: 1.5rem;
        box-shadow: 0 2px 16px rgba(0,0,0,0.07);
        margin-bottom: 1.2rem;
        border-left: 4px solid #667eea;
    }
    .result-card h3 {
        color: #667eea;
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
    }
    .result-card p  { font-size: 1rem; color: #1a1a2e; line-height: 1.6; margin: 0; }

    .price-card {
        background: linear-gradient(135deg, #11998e, #38ef7d);
        border-radius: 14px;
        padding: 1.5rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 20px rgba(17,153,142,0.3);
    }
    .price-card .price-label { font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; opacity: 0.85; }
    .price-card .price-value { font-size: 2.8rem; font-weight: 700; margin: 0.3rem 0; }
    .price-card .price-range { font-size: 0.85rem; opacity: 0.8; }

    .tag-pill {
        display: inline-block;
        background: #f0f2ff;
        color: #667eea;
        border: 1px solid #c7d2fe;
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 0.82rem;
        font-weight: 500;
        margin: 3px;
    }

    .badge {
        display: inline-block;
        background: #fef3c7;
        color: #92400e;
        border-radius: 6px;
        padding: 3px 10px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-bottom: 0.8rem;
    }

    .upload-hint {
        background: #f0f4ff;
        border: 2px dashed #c7d2fe;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        color: #6b7280;
        font-size: 0.9rem;
    }

    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        width: 100%;
        transition: opacity 0.2s;
    }
    .stButton > button:hover { opacity: 0.88; }

    .sidebar-info {
        background: #f0f4ff;
        border-radius: 10px;
        padding: 1rem;
        font-size: 0.83rem;
        color: #374151;
        line-height: 1.6;
    }

    .metric-row {
        display: flex;
        gap: 0.8rem;
        margin-bottom: 1.2rem;
    }
    .metric-box {
        flex: 1;
        background: white;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
    }
    .metric-box .m-val { font-size: 1.5rem; font-weight: 700; color: #667eea; }
    .metric-box .m-lbl { font-size: 0.73rem; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.5px; }

    div[data-testid="stImage"] img { border-radius: 12px; }
</style>
""", unsafe_allow_html=True)


# ─── Helpers ────────────────────────────────────────────────────────────────
def configure_gemini(api_key: str):
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.0-flash")


SYSTEM_PROMPT = """
You are an expert e-commerce product analyst and copywriter. Your job is to analyze product images
and generate compelling, SEO-friendly product listings.

Given an image of a product, return ONLY a valid JSON object (no markdown, no backticks) with these keys:

{
  "title": "Short, punchy product title (5-10 words max)",
  "category": "Main product category (e.g., Clothing, Electronics, Footwear)",
  "description": "2-3 sentence compelling product description highlighting key features, material, style, and use cases. Be specific and persuasive.",
  "bullet_points": ["Feature 1", "Feature 2", "Feature 3", "Feature 4"],
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
  "color": "Primary color(s) of the product",
  "condition": "New",
  "recommended_price_usd": 29.99,
  "price_range_low": 19.99,
  "price_range_high": 44.99,
  "price_rationale": "1 sentence explaining why this price is fair for this type of product",
  "seo_title": "SEO-optimized title with keywords",
  "target_audience": "Who this product is best for"
}

Be realistic with pricing. Base prices on typical market rates for the product type.
Respond with ONLY the JSON object — no extra text.
"""


def analyze_product(model, image: Image.Image) -> dict:
    """Send image to Gemini and parse the JSON response."""
    response = model.generate_content([SYSTEM_PROMPT, image])
    raw = response.text.strip()

    # Strip markdown fences if present
    raw = re.sub(r"^```(?:json)?", "", raw, flags=re.MULTILINE)
    raw = re.sub(r"```$", "", raw, flags=re.MULTILINE)
    raw = raw.strip()

    return json.loads(raw)


def format_price(val) -> str:
    try:
        return f"${float(val):,.2f}"
    except Exception:
        return str(val)


# ─── Sidebar ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
input[type="password"]::-ms-reveal,
input[type="password"]::-ms-clear {
    display: none;
}

[data-testid="stTextInput"] button {
    display: none;
}
</style>
""", unsafe_allow_html=True)
with st.sidebar:
    st.markdown("## Configuration")
    api_key = st.text_input(
        "Google Gemini API Key",
        type="password",
        placeholder="AIza... or AQ...",
        help="Get your free key at https://aistudio.google.com — both AIza and AQ key formats are valid.",
    )
    st.markdown("---")
    st.markdown("### Currency")
    currency = st.selectbox("Display prices in", ["USD ($)", "EUR (€)", "GBP (£)", "PKR (₨)", "INR (₹)"])
    currency_map = {"USD ($)": ("$", 1), "EUR (€)": ("€", 0.92), "GBP (£)": ("£", 0.79), "PKR (₨)": ("₨", 278), "INR (₹)": ("₹", 83)}
    sym, rate = currency_map[currency]

    st.markdown("---")
    st.markdown("### About This App")
    st.markdown("""
<div class='sidebar-info'>
<b>ShopVision AI</b> uses Google's Gemini 1.5 Flash multimodal model to analyze product photos and instantly generate:
<br><br>
Product titles & descriptions<br>
SEO keywords & tags<br>
Recommended pricing<br>
Target audience insights<br>
<br>
<b>Powered by:</b> Gemini 1.5 Flash<br>
<b>Free tier:</b> 15 req/min, 1500/day
</div>
""", unsafe_allow_html=True)

# ─── Hero Banner ─────────────────────────────────────────────────────────────
st.markdown("""
<div class='hero-banner'>
    <h1>Product Caption Generator</h1>
    <p>Upload a product photo → Get instant titles, descriptions & pricing powered by AI</p>
</div>
""", unsafe_allow_html=True)

# ─── Main Layout ─────────────────────────────────────────────────────────────
col_upload, col_results = st.columns([1, 1.6], gap="large")

with col_upload:
    st.markdown("### 📷 Upload Product Image")
    uploaded_file = st.file_uploader(
        "Choose an image",
        type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed",
    )

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, use_container_width=True, caption="Your product")

        # File info
        size_kb = uploaded_file.size / 1024
        st.markdown(f"""
<div class='metric-row'>
  <div class='metric-box'><div class='m-val'>{image.width}</div><div class='m-lbl'>Width px</div></div>
  <div class='metric-box'><div class='m-val'>{image.height}</div><div class='m-lbl'>Height px</div></div>
  <div class='metric-box'><div class='m-val'>{size_kb:.0f}</div><div class='m-lbl'>KB</div></div>
</div>
""", unsafe_allow_html=True)

        if st.button("🚀 Generate Listing"):
            if not api_key:
                st.error("Please enter your Gemini API key in the sidebar.")
            else:
                with st.spinner("🔍 Analyzing your product..."):
                    try:
                        model = configure_gemini(api_key)
                        data = analyze_product(model, image)
                        st.session_state["result"] = data
                        st.session_state["sym"] = sym
                        st.session_state["rate"] = rate
                        st.success("Analysis complete!")
                    except json.JSONDecodeError as e:
                        st.error(f"JSON parse error: {e}")
                    except Exception as e:
                        st.error(f"Error: {e}")
    else:
        st.markdown("""
<div class='upload-hint'>
    <div style='font-size:2.5rem'>📦</div>
    <div style='font-weight:600; margin-top:0.5rem'>Drop your product image here</div>
    <div>JPG, PNG, WEBP supported</div>
</div>
""", unsafe_allow_html=True)


with col_results:
    if "result" in st.session_state:
        d = st.session_state["result"]
        s = st.session_state["sym"]
        r = st.session_state["rate"]

        def px(v): return f"{s}{float(v)*r:,.2f}"

        st.markdown("### 🎯 Generated Listing")
        st.markdown(f"<span class='badge'> {d.get('category','Product')}</span>", unsafe_allow_html=True)

        # Title
        st.markdown(f"""
<div class='result-card'>
    <h3>Product Title</h3>
    <p style='font-size:1.25rem; font-weight:600;'>{d.get('title','')}</p>
</div>""", unsafe_allow_html=True)

        # SEO Title
        st.markdown(f"""
<div class='result-card'>
    <h3>SEO Title</h3>
    <p>{d.get('seo_title','')}</p>
</div>""", unsafe_allow_html=True)

        # Description
        st.markdown(f"""
<div class='result-card'>
    <h3>Product Description</h3>
    <p>{d.get('description','')}</p>
</div>""", unsafe_allow_html=True)

        # Bullet points
        bullets_html = "".join([f"<li style='margin:4px 0'>{b}</li>" for b in d.get("bullet_points", [])])
        st.markdown(f"""
<div class='result-card'>
    <h3>Key Features</h3>
    <ul style='margin:0; padding-left:1.2rem; color:#1a1a2e;'>{bullets_html}</ul>
</div>""", unsafe_allow_html=True)

        # Price card
        st.markdown(f"""
<div class='price-card'>
    <div class='price-label'>💰 Recommended Price</div>
    <div class='price-value'>{px(d.get('recommended_price_usd', 0))}</div>
    <div class='price-range'>Market Range: {px(d.get('price_range_low', 0))} – {px(d.get('price_range_high', 0))}</div>
    <div style='margin-top:0.7rem; font-size:0.85rem; opacity:0.85;'>💡 {d.get('price_rationale','')}</div>
</div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Tags + details
        col_a, col_b = st.columns(2)
        with col_a:
            tags_html = "".join([f"<span class='tag-pill'>{t}</span>" for t in d.get("tags", [])])
            st.markdown(f"""
<div class='result-card'>
    <h3>Tags</h3>
    <div>{tags_html}</div>
</div>""", unsafe_allow_html=True)

        with col_b:
            st.markdown(f"""
<div class='result-card'>
    <h3>Details</h3>
    <p><b>Color:</b> {d.get('color','—')}<br>
    <b>Condition:</b> {d.get('condition','New')}<br>
    <b>Audience:</b> {d.get('target_audience','—')}</p>
</div>""", unsafe_allow_html=True)

        # Export JSON
        st.markdown("---")
        json_str = json.dumps(d, indent=2)
        st.download_button(
            label="📥 Download as JSON",
            data=json_str,
            file_name="product_listing.json",
            mime="application/json",
            use_container_width=True,
        )

    else:
        st.markdown("""
<div style='text-align:center; padding: 4rem 2rem; color: #9ca3af;'>
    <div style='font-size:4rem'>✨</div>
    <div style='font-size:1.1rem; font-weight:500; margin-top:1rem;'>Your AI-generated listing will appear here</div>
    <div style='font-size:0.9rem; margin-top:0.5rem;'>Upload a product image and click Generate</div>
</div>
""", unsafe_allow_html=True)

# ─── Footer ──────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center; color:#9ca3af; font-size:0.82rem; padding:0.5rem 0 1rem;'>
    ShopVision AI · Powered by Google Gemini 1.5 Flash · Built with Streamlit
</div>
""", unsafe_allow_html=True)