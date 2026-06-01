# 🛍️ ShopVision AI — E-Commerce Caption Generator

> Upload a product photo → Get an AI-generated title, description, tags & recommended price instantly.

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Get your FREE Gemini API key
1. Visit **https://aistudio.google.com/app/apikey**
2. Sign in with your Google account
3. Click **"Create API Key"** — it's completely free
4. Copy the key (starts with `AIza...`)

### 3. Run the app
```bash
streamlit run app.py
```

4. Paste your API key in the **sidebar** and upload a product image!

---

## 📁 Project Structure

```
ecommerce_caption_generator/
├── app.py              ← Main Streamlit application
├── requirements.txt    ← Python dependencies
└── README.md           ← This file
```

---

## 🎓 Presentation Content

### 📌 Project Title
**ShopVision AI: Automated E-Commerce Product Listing Generator using Multimodal Large Language Models**

---

### 🔬 Model Information

| Property | Details |
|---|---|
| **Model Name** | Google Gemini 1.5 Flash |
| **Developer** | Google DeepMind |
| **Model Type** | Multimodal Large Language Model (MLLM) |
| **Architecture** | Transformer-based, Mixture of Experts (MoE) |
| **Context Window** | 1,000,000 tokens |
| **Modalities** | Text, Image, Video, Audio, Code |
| **Release Date** | May 2024 |
| **API Access** | Free tier via Google AI Studio |

---

### 📚 Training Data

Gemini 1.5 Flash was trained on a massive, diverse multimodal dataset including:

- **Web Text**: Trillions of tokens from Common Crawl, books, Wikipedia, and code repositories
- **Image-Text Pairs**: Hundreds of millions of image-caption pairs from the web (CC12M, LAION-400M style datasets)
- **Product Catalogs**: E-commerce and retail image datasets
- **Multilingual Data**: Over 100 languages
- **Code**: GitHub repositories across 80+ programming languages
- **Scientific Papers**: ArXiv, PubMed, and academic journals

> Google has not disclosed the exact dataset composition, but estimates suggest 10–15 trillion tokens of text and billions of image-text pairs.

---

### 🧠 How It Works — Technical Flow

```
User uploads image
        │
        ▼
Image encoded as base64 bytes
        │
        ▼
Sent to Gemini 1.5 Flash via Google Generative AI API
        │
        ▼
Vision encoder (ViT-style) extracts image features
        │
        ▼
Language model fuses image tokens + text prompt
        │
        ▼
Generates structured JSON output:
 ├─ Product Title
 ├─ SEO Title
 ├─ Description
 ├─ Bullet Points
 ├─ Tags / Keywords
 ├─ Target Audience
 └─ Recommended Price + Range
        │
        ▼
Streamlit UI renders the results
```

---

### 🏗️ Architecture Overview

**Gemini 1.5 Flash** uses a novel **Mixture of Experts (MoE)** architecture:
- Uses **selective expert activation** — only a subset of parameters are activated per token, enabling speed and efficiency
- **Long-context understanding** via efficient attention mechanisms (up to 1M token context)
- Separate **vision encoder** processes image patches into visual tokens
- Visual tokens are merged into the main transformer stream via **cross-attention layers**
- Output: auto-regressive token generation

---

### 🆓 API Free Tier Details

| Limit | Value |
|---|---|
| Requests per minute | 15 RPM |
| Requests per day | 1,500 RPD |
| Tokens per minute | 1,000,000 TPM |
| Price | **FREE** (no credit card needed) |

---

### 🌟 Key Features of the Application

1. **Zero Training Required** — leverages pre-trained Gemini model via API
2. **Multimodal AI** — understands both visual content and generates natural language
3. **Structured Output** — enforced JSON schema for consistent results
4. **Multi-currency Support** — USD, EUR, GBP, PKR, INR
5. **SEO-Optimized** — generates both display titles and SEO-friendly titles
6. **Export Functionality** — download results as JSON for integration
7. **Responsive UI** — built with Streamlit + custom CSS

---

### 📊 Why Gemini 1.5 Flash vs Alternatives?

| Model | Free Tier | Vision | Speed | Product Listing Quality |
|---|---|---|---|---|
| **Gemini 1.5 Flash** ✅ | ✅ Yes | ✅ Native | ⚡ Very Fast | ⭐⭐⭐⭐⭐ |
| GPT-4o (OpenAI) | ❌ Paid | ✅ Native | Fast | ⭐⭐⭐⭐⭐ |
| Claude 3 Haiku | ❌ Paid | ✅ Native | Very Fast | ⭐⭐⭐⭐ |
| LLaVA (local) | ✅ Yes | ✅ Native | Slow (local) | ⭐⭐⭐ |
| BLIP-2 (local) | ✅ Yes | ✅ Native | Medium | ⭐⭐⭐ |

**Gemini 1.5 Flash chosen** because: free tier, fast inference, excellent instruction following, reliable JSON output.

---

### 🎯 Use Cases

- **Individual sellers** on Daraz, Amazon, Etsy, eBay
- **Small businesses** without a copywriting team
- **Warehouse automation** — bulk product listing generation
- **Marketplace onboarding** — help new sellers list products faster

---

### 🔮 Future Improvements

1. Batch processing (multiple products at once)
2. Direct integration with WooCommerce / Shopify APIs
3. A/B testing of generated titles
4. Fine-tuned pricing model trained on actual sales data
5. Background removal before analysis
6. Competitor price scraping for better price recommendations

---

*Built with ❤️ using Python, Streamlit, and Google Gemini 1.5 Flash*
