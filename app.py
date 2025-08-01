import streamlit as st
import os
import torchvision.transforms as transforms
import numpy as np
import sys
import speech_recognition as sr
import pyttsx3
import google.generativeai as genai
from google.generativeai.types.content_types import to_part
from PIL import Image
import io
import torch
import pandas as pd
import plotly.express
import csv
import hashlib
import time

# ✅ Corrected CLIP import
sys.path.append(os.path.abspath("clip_openai"))
import clip  # This fixes the "AttributeError: module 'clip' has no attribute 'load'"

# Load CLIP model with memory optimization
device = "cuda" if torch.cuda.is_available() else "cpu"
try:
    # Use ViT-B/32 (as per your updated preference)
    clip_model, preprocess = clip.load("ViT-B/32", device=device, download_root=os.path.expanduser("~/.cache/clip"))
except Exception as e:
    st.error(f"Error loading CLIP model: {e}. Falling back to CPU with ViT-B/32.")
    device = "cpu"
    clip_model, preprocess = clip.load("ViT-B/32", device=device, download_root=os.path.expanduser("~/.cache/clip"))

# Custom download verification with chunked reading
def verify_file_hash(file_path, expected_sha256, chunk_size=8192):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        while True:
            data = f.read(chunk_size)
            if not data:
                break
            sha256_hash.update(data)
    return sha256_hash.hexdigest() == expected_sha256

# Add src to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.database import products, save_to_csv
from src.order_utils import save_order_to_csv, generate_invoice_pdf

# Configure Gemini API
genai.configure(api_key="AIzaSyDO_jMqVWh-htHXr4P5nMZNXa9w4LZPX9Y")  # Replace with your API key

# Initialize TTS engine (moved to session state)
if "tts_engine" not in st.session_state:
    st.session_state.tts_engine = pyttsx3.init()

# Initialize Gemini Vision Model
gemini_model = genai.GenerativeModel("models/gemini-1.5-flash")

# Language translations
translations = {
    "en": {
        "title": "D.Watson Smart Assistant 🤖💬",
        "header": "Your One-Stop Shop for Health, Beauty & More!",
        "search_placeholder": "Enter product name or question:",
        "search_button": "Search",
        "voice_button": "Voice 🎙️",
        "product_details": "📦 Product Details",
        "price": "Price",
        "available": "Available",
        "category": "Category",
        "description": "Gemini Description",
        "read_info": "🔊 Read Product Info",
        "stop": "🛑 Stop",
        "add_to_cart": "Add to Cart",
        "your_cart": "🛒 Your Cart",
        "total": "Total",
        "clear_cart": "Clear Cart",
        "proceed_checkout": "Proceed to Checkout",
        "checkout_summary": "💳 Checkout Summary",
        "payment_type": "Choose Payment Type:",
        "cash_on_delivery": "Cash on Delivery",
        "online_payment": "Online Payment",
        "online_method": "Select Online Payment Method",
        "send_otp": "📩 Send OTP",
        "verify_otp": "✅ Verify OTP",
        "confirm_payment": "Confirm Payment",
        "upload_image": "📷 Upload product image",
        "closest_match": "🔍 Closest Match",
        "not_found": "❌ Product not found in your inventory.",
        "categories": "Categories",
        "select_category": "Select Category",
        "manage_inventory": "Manage Inventory",
        "select_product": "Select Product to Update",
        "update_quantity": "Update Quantity",
        "dashboard": "📊 Sales & Inventory Dashboard",
        "sales_summary": "💰 Sales Summary",
        "total_orders": "Total Orders",
        "total_income": "Total Income",
        "sales_by_product": "📈 Sales by Product",
        "sales_distribution": "🥧 Sales Distribution by Product",
        "sales_trend": "📉 Sales Trend Over Time",
        "inventory_value": "📦 Inventory Value",
        "low_stock": "🚨 Low Stock Items",
        "reviews": "Reviews and Ratings ⭐",
        "submit_review": "Submit Review",
        "rating": "Rating",
        "comment": "Comment",
        "no_reviews": "No reviews yet.",
        "avg_rating": "Average Rating",
        "payable": "Payable",
        "suggestion": "Submit a Suggestion 💬",
        "suggestion_placeholder": "Enter your suggestion here...",
        "submit_suggestion": "Submit Suggestion",
        "suggestion_success": "Thank you for your suggestion!",
    },
    "ur": {
        "title": "ڈی واٹسن سمارٹ اسسٹنٹ 🤖💬",
        "header": "صحت، خوبصورتی اور مزید کے لیے ایک ہی دکان!",
        "search_placeholder": "پروڈکٹ کا نام یا سوال درج کریں:",
        "search_button": "تلاش کریں",
        "voice_button": "آواز 🎙️",
        "product_details": "📦 پروڈکٹ کی تفصیلات",
        "price": "قیمت",
        "available": "دستیاب",
        "category": "قسم",
        "description": "جمنی کی تفصیل",
        "read_info": "🔊 پروڈکٹ کی معلومات پڑھیں",
        "stop": "🛑 روکیں",
        "add_to_cart": "کارٹ میں شامل کریں",
        "your_cart": "🛒 آپ کا کارٹ",
        "total": "کل",
        "clear_cart": "کارٹ خالی کریں",
        "proceed_checkout": "چیک آؤٹ کے لیے آگے بڑھیں",
        "checkout_summary": "💳 چیک آؤٹ خلاصہ",
        "payment_type": "ادائیگی کا طریقہ منتخب کریں:",
        "cash_on_delivery": "ڈلیوری پر نقد ادائیگی",
        "online_payment": "آن لائن ادائیگی",
        "online_method": "آن لائن ادائیگی کا طریقہ منتخب کریں",
        "send_otp": "📩 OTP بھیجیں",
        "verify_otp": "✅ OTP تصدیق کریں",
        "confirm_payment": "ادائیگی کی تصدیق کریں",
        "upload_image": "📷 پروڈکٹ کی تصویر اپ لوڈ کریں",
        "closest_match": "🔍 سب سے قریبی میچ",
        "not_found": "❌ انوینٹری میں پروڈکٹ نہیں ملا۔",
        "categories": "اقسام",
        "select_category": "قسم منتخب کریں",
        "manage_inventory": "انوینٹری کا انتظام",
        "select_product": "اپ ڈیٹ کرنے کے لیے پروڈکٹ منتخب کریں",
        "update_quantity": "مقدار اپ ڈیٹ کریں",
        "dashboard": "📊 سیلز اور انوینٹری ڈیش بورڈ",
        "sales_summary": "💰 سیلز خلاصہ",
        "total_orders": "کل آرڈرز",
        "total_income": "کل آمدنی",
        "sales_by_product": "📈 پروڈکٹ کے لحاظ سے سیلز",
        "sales_distribution": "🥧 پروڈکٹ کے لحاظ سے سیلز تقسیم",
        "sales_trend": "📉 وقت کے ساتھ سیلز رجحان",
        "inventory_value": "📦 انوینٹری کی قدر",
        "low_stock": "🚨 کم اسٹاک آئٹمز",
        "reviews": "⭐ جائزے اور درجہ بندی",
        "submit_review": "جائزہ جمع کروائیں",
        "rating": "درجہ بندی",
        "comment": "تبصرہ",
        "no_reviews": "ابھی تک کوئی جائزہ نہیں۔",
        "avg_rating": "اوسط درجہ بندی",
        "payable": "ادائیگی کے قابل",
        "suggestion": "تجویز جمع کروائیں",
        "suggestion_placeholder": "اپنی تجویز یہاں درج کریں...",
        "submit_suggestion": "تجویز جمع کریں",
        "suggestion_success": "آپ کی تجویز کے لیے شکریہ!",
    }
}

# OTP Session
if "otp_sent" not in st.session_state:
    st.session_state.otp_sent = False
if "generated_otp" not in st.session_state:
    st.session_state.generated_otp = ""
if "otp_verified" not in st.session_state:
    st.session_state.otp_verified = False

# Session State Setup
if "query" not in st.session_state:
    st.session_state.query = ""
if "cart" not in st.session_state:
    st.session_state.cart = {}
if "last_product_key" not in st.session_state:
    st.session_state.last_product_key = None
if "last_product_description" not in st.session_state:
    st.session_state.last_product_description = ""
if "reading" not in st.session_state:
    st.session_state.reading = False
if "language" not in st.session_state:
    st.session_state.language = "en"  # Default language
if "selected_rating" not in st.session_state:
    st.session_state.selected_rating = 0  # Default rating

# Function to get average rating
def get_average_rating(product_key):
    reviews_file = "reviews.csv"
    if os.path.exists(reviews_file):
        df = pd.read_csv(reviews_file)
        reviews = df[df["product_key"] == product_key]
        return reviews["rating"].mean() if not reviews.empty else 0
    return 0

# Function to save review
def save_review(product_key, rating, comment):
    reviews_file = "reviews.csv"
    timestamp = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    if not os.path.exists(reviews_file):
        with open(reviews_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["product_key", "rating", "comment", "timestamp"])
    with open(reviews_file, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([product_key, rating, comment, timestamp])

# Sidebar Navigation
page = st.sidebar.radio(translations[st.session_state.language]["dashboard"], ["Shop Assistant", "Dashboard"])

# Sidebar Content (Persistent across all pages)
st.sidebar.header(translations[st.session_state.language]["categories"])
categories = set(product["category"] for product in products.values())
selected_category = st.sidebar.selectbox(translations[st.session_state.language]["select_category"], ["All"] + list(categories))

st.sidebar.header(translations[st.session_state.language]["manage_inventory"])
product_to_update = st.sidebar.selectbox(translations[st.session_state.language]["select_product"], list(products.keys()))
new_quantity = st.sidebar.number_input(translations[st.session_state.language]["update_quantity"], min_value=0, value=products[product_to_update]["quantity"])
if st.sidebar.button(translations[st.session_state.language]["update_quantity"]):
    products[product_to_update]["quantity"] = new_quantity
    save_to_csv()
    st.sidebar.success(f"{products[product_to_update]['name']} updated to {new_quantity}!")

# Language selector
st.session_state.language = st.sidebar.selectbox("Language / زبان", ["en", "ur"])

# Reviews and Ratings Section in Sidebar
st.sidebar.header(translations[st.session_state.language]["reviews"])
product_key = st.session_state.last_product_key
st.sidebar.write(f"Debug: product_key = {product_key}")  # Debug to check value
if product_key and product_key in products:
    avg_rating = get_average_rating(product_key)
    st.sidebar.write(f"{translations[st.session_state.language]['avg_rating']}: {avg_rating:.1f}/5")

    df_reviews = pd.read_csv("reviews.csv") if os.path.exists("reviews.csv") else pd.DataFrame()
    product_reviews = df_reviews[df_reviews["product_key"] == product_key]
    if not product_reviews.empty:
        for _, row in product_reviews.iterrows():
            st.sidebar.write(f"- Rating: {row['rating']}/5, Comment: {row['comment']}")
    else:
        st.sidebar.write(translations[st.session_state.language]["no_reviews"])

    # Review Submission with Clickable Stars
    with st.sidebar.expander(translations[st.session_state.language]["submit_review"]):
        # Container for horizontal star buttons with reduced size
        with st.sidebar.container():
            # Use columns with reduced width for horizontal layout
            cols = st.sidebar.columns([0.8, 0.8, 0.8, 0.8, 0.8])  # Reduced width for each column
            for i in range(5):
                with cols[i]:
                    st.sidebar.button("★", key=f"star_{i}", on_click=lambda x=i: setattr(st.session_state, "selected_rating", x + 1), help=f"Rate {i+1}")

        # Display stars with selection visually in a horizontal line
        stars_html = "".join(
            f'<span class="star {(st.session_state.selected_rating > i and "selected" or "")}">★</span>'
            for i in range(5)
        )
        st.sidebar.markdown(f'<div style="display: flex; margin-top: 5px; justify-content: flex-start;">{stars_html}</div>', unsafe_allow_html=True)

        # Add CSS for styling with reduced button size
        st.sidebar.markdown("""
            <style>
            .star {
                font-size: 24px;
                cursor: pointer;
                display: inline-block;
                margin-right: 5px;
                color: gray;
            }
            .star.selected {
                color: gold;
            }
            button[title*="star"] {
                background-color: purple;
                color: white;
                border: none;
                padding: 2px 6px; /* Reduced padding */
                margin: 0;
                width: 100%;
                font-size: 18px; /* Reduced font size */
                text-align: center;
                min-width: 20px; /* Minimum width to fit star */
            }
            button[title*="star"]:hover {
                background-color: darkpurple;
            }
            </style>
        """, unsafe_allow_html=True)

        comment = st.sidebar.text_input(translations[st.session_state.language]["comment"])
        if st.sidebar.button(translations[st.session_state.language]["submit_review"]):
            if st.session_state.selected_rating > 0 and comment.strip():
                save_review(product_key, st.session_state.selected_rating, comment)
                st.session_state.selected_rating = 0  # Reset rating after submission
                st.sidebar.success("Review submitted!")
                st.rerun()
            else:
                st.sidebar.error("Please select a rating and enter a comment.")

# Suggestion feature in Sidebar
st.sidebar.header(translations[st.session_state.language]["suggestion"])
suggestion = st.sidebar.text_input(translations[st.session_state.language]["suggestion_placeholder"])
if st.sidebar.button(translations[st.session_state.language]["submit_suggestion"]):
    if suggestion.strip():
        with open("suggestions.csv", "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([suggestion.strip(), pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")])
        st.sidebar.success(translations[st.session_state.language]["suggestion_success"])
        suggestion = ""  # Clear input after submission
    else:
        st.sidebar.error("Please enter a suggestion.")

# ==================== PAGE: DASHBOARD ====================
if page == "Dashboard":
    st.title(translations[st.session_state.language]["dashboard"])
    st.markdown("""
        <style>
        .stApp { background-color: #f0f8ff; padding: 20px; }
        .stSuccess { background-color: #d4edda; padding: 10px; border-radius: 5px; }
        .st-emotion-cache-1rwb540 {
        background-color: #90ee90; color: black;
        }
        .st-emotion-cache-1h08hrp { background-color: purple; color: white; }
        .st-emotion-cache-jx6q2s { background-color: #add8e6; }
        .st-emotion-cache-1w723zb { background-color: #87ceeb; }
        body { background-color: #e6f3ff; }
        .st-emotion-cache-4rsbii { background-color: #b0e0e6; }
        .st-emotion-cache-14vh5up { background-color: lightseagreen; }
        .st-emotion-cache-1t8vfw5 h1, .st-emotion-cache-1t8vfw5 span { color: black; }
        .st-emotion-cache-9fqyt2 p, .st-emotion-cache-9fqyt2 li { color: black; }
        .st-emotion-cache-pp1cl0 p, .st-emotion-cache-pp1cl0 li { color: black; }
        button[data-testid="baseButton-secondary"][title="Update Quantity"] { background-color: #32cd32 !important; color: white !important; }
        .stSidebar { background-color: #87ceeb !important; }
        .star { font-size: 24px; cursor: pointer; display: inline-block; margin-right: 5px; }
        .star.selected { color: gold; }
        </style>
    """, unsafe_allow_html=True)

    try:
        df = pd.read_csv("order_history.csv")

        expected_cols = {"timestamp", "product", "quantity", "price"}
        if not expected_cols.issubset(set(df.columns)):
            st.error("⚠️ The order file does not contain the required columns.")
            st.stop()

        df["total"] = df["quantity"] * df["price"]
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        st.subheader(translations[st.session_state.language]["sales_summary"])
        st.write(f"{translations[st.session_state.language]['total_orders']}: {len(df)}")
        st.write(f"{translations[st.session_state.language]['total_income']}: Rs.{df['total'].sum():,.0f}")

        st.subheader(translations[st.session_state.language]["sales_by_product"])
        product_sales = df.groupby("product").agg({"quantity": "sum", "total": "sum"})
        st.bar_chart(product_sales["quantity"])

        st.subheader(translations[st.session_state.language]["sales_distribution"])
        fig = plotly.express.pie(names=product_sales.index, values=product_sales["total"], title=translations[st.session_state.language]["sales_distribution"])
        st.plotly_chart(fig)

        st.subheader(translations[st.session_state.language]["sales_trend"])
        sales_trend = df.groupby(df["timestamp"].dt.date).agg({"total": "sum"})
        st.line_chart(sales_trend["total"])

        st.subheader(translations[st.session_state.language]["inventory_value"])
        inventory_data = {k: v["quantity"] * v["price"] for k, v in products.items()}
        st.bar_chart(pd.Series(inventory_data))

        low_stock = {k: v for k, v in {k: products[k]["quantity"] for k in products}.items() if v < 5}
        if low_stock:
            st.warning(translations[st.session_state.language]["low_stock"])
            for k, v in low_stock.items():
                st.write(f"- {products[k]['name']}: {v} left")

    except FileNotFoundError:
        st.warning("No sales data found yet. Make a sale to generate dashboard!")

# ==================== PAGE: SHOP ASSISTANT ====================
else:
    st.title(translations[st.session_state.language]["title"])
    st.header(translations[st.session_state.language]["header"])
    st.markdown("""
        <style>
        .stApp { background-color: #f5f5f5; padding: 20px; }
        .stSuccess { background-color: #d4edda; padding: 10px; border-radius: 5px; }
        .st-emotion-cache-1rwb540 { background-color: purple; color: white; }
        .st-emotion-cache-1h08hrp { background-color: purple; color: white; }
        .st-emotion-cache-jx6q2s { background-color: cyan; }
        .st-emotion-cache-1w723zb { background-color: #5478f0; }
        body { background-color: brown; }
        .st-emotion-cache-4rsbii { background-color: #7adcfa; }
        .st-emotion-cache-14vh5up { background-color: lightgray; }
        .st-emotion-cache-1t8vfw5 h1, .st-emotion-cache-1t8vfw5 span { color: white; }
        .st-emotion-cache-9fqyt2 p, .st-emotion-cache-9fqyt2 li { color: white; }
        .st-emotion-cache-pp1cl0 p, .st-emotion-cache-pp1cl0 li { color: white; }
        button[data-testid="baseButton-secondary"][title="Update Quantity"] { background-color: #00ced1 !important; color: white !important; }
        .stSidebar { background-color: cyan !important; }
        .star { font-size: 24px; cursor: pointer; display: inline-block; margin-right: 5px; }
        .star.selected { color: gold; }
        </style>
    """, unsafe_allow_html=True)

    # Search Bar
    query = st.text_input(translations[st.session_state.language]["search_placeholder"], value=st.session_state.query)
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button(translations[st.session_state.language]["search_button"]):
            st.session_state.query = query.strip().lower()
            filtered = products if selected_category == "All" else {
                k: v for k, v in products.items() if v["category"] == selected_category
            }
            if st.session_state.query in filtered:
                st.session_state.last_product_key = st.session_state.query
                gemini_response = gemini_model.generate_content(
                    f"Write a short 4-5 line description about the product {st.session_state.query} in 50 words only"
                )
                st.session_state.last_product_description = gemini_response.text
            else:
                st.session_state.last_product_key = None
                st.session_state.last_product_description = ""
                response = gemini_model.generate_content(f"Tell me about {query}")
                st.info(response.text)

    with col2:
        if st.button(translations[st.session_state.language]["voice_button"]):
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                st.write("Listening...")
                try:
                    recognizer.adjust_for_ambient_noise(source, duration=1)
                    audio = recognizer.listen(source, timeout=5)
                    voice_input = recognizer.recognize_google(audio).lower().strip()
                    st.session_state.query = voice_input
                    st.rerun()
                except Exception as e:
                    st.error(f"Mic error: {e}")

    # Display Product
    product_key = st.session_state.last_product_key
    if product_key and product_key in products:
        product = products[product_key]
        description = (
            st.session_state.last_product_description
            if st.session_state.last_product_description
            else translations[st.session_state.language]["no_reviews"]
        )

        with st.expander(translations[st.session_state.language]["product_details"], expanded=True):
            st.markdown(f"<div class='stSuccess'>✅ <b>{product['name']}</b></div>", unsafe_allow_html=True)
            st.write(f"- **{translations[st.session_state.language]['price']}:** Rs.{product['price']}")
            st.write(f"- **{translations[st.session_state.language]['available']}:** {product['quantity']} units")
            st.write(f"- **{translations[st.session_state.language]['category']}:** {product['category']}")
            st.markdown(f"**{translations[st.session_state.language]['description']}:** {description}")

        # Buttons for Read/Stop (Global TTS engine management)
        if "tts_engine" not in st.session_state:
            st.session_state.tts_engine = pyttsx3.init()

        tts_info = (
            f"{product['name']}, {translations[st.session_state.language]['price']} rupees {product['price']}, "
            f"{translations[st.session_state.language]['available']} {product['quantity']}, "
            f"{translations[st.session_state.language]['category']} {product['category']}. "
            f"{translations[st.session_state.language]['description']}: {description}"
        )

        col_tts1, col_tts2 = st.columns([1, 1])
        with col_tts1:
            if st.button(translations[st.session_state.language]["read_info"], key="read_info"):
                if not st.session_state.get("reading", False):
                    st.session_state.reading = True
                    tts_engine = st.session_state.tts_engine
                    tts_engine.stop()  # Stop any ongoing speech
                    tts_engine.say(tts_info)
                    tts_engine.runAndWait()  # Synchronous TTS execution
                    import time
                    time.sleep(0.1)  # Small delay to ensure TTS completes
                    st.session_state.reading = False
                    st.rerun()  # Refresh to clear loading state

        with col_tts2:
            if st.button(translations[st.session_state.language]["stop"], key="stop"):
                st.session_state.reading = False
                tts_engine = st.session_state.tts_engine
                tts_engine.stop()  # Stop any ongoing speech
                st.rerun()  # Refresh to clear loading state

        # Show Add to Cart only when not reading
        if not st.session_state.reading:
            if st.button(translations[st.session_state.language]["add_to_cart"], key="add_to_cart"):
                if product_key in st.session_state.cart:
                    st.session_state.cart[product_key] += 1
                else:
                    st.session_state.cart[product_key] = 1
                st.success(f"{product['name']} added to cart!")

    # ✅ Show cart
    if st.session_state.cart:
        st.subheader(translations[st.session_state.language]["your_cart"])
        total = 0
        for item in st.session_state.cart:
            qty = st.session_state.cart[item]
            price = products[item]["price"]
            total += qty * price
            st.write(f"- {products[item]['name']} (Qty: {qty}) - Rs.{price} each")
        st.write(f"**{translations[st.session_state.language]['total']}: Rs.{total}**")

        col_cart1, col_cart2 = st.columns([1, 1])
        with col_cart1:
            if st.button(translations[st.session_state.language]["clear_cart"], key="clear_cart"):
                st.session_state.cart = {}
                st.success("Cart cleared!")
        with col_cart2:
            if st.button(translations[st.session_state.language]["proceed_checkout"], key="proceed_checkout"):
                st.session_state.checkout = True

    # ✅ Checkout Modal / Section with Advanced Payment Options
    if st.session_state.get("checkout", False):
        if st.session_state.cart:
            st.subheader(translations[st.session_state.language]["checkout_summary"])

            total = sum(products[item]["price"] * qty for item, qty in st.session_state.cart.items())

            for item, qty in st.session_state.cart.items():
                st.write(f"{products[item]['name']} - Qty: {qty} - Rs.{products[item]['price']} each")
            st.write(f"**{translations[st.session_state.language]['total']} {translations[st.session_state.language]['payable']}: Rs.{total}**")

            payment_type = st.radio(translations[st.session_state.language]["payment_type"], 
                                   [translations[st.session_state.language]["cash_on_delivery"], 
                                    translations[st.session_state.language]["online_payment"]], 
                                   key="payment_type_1")

            valid_payment = True

            if payment_type == translations[st.session_state.language]["online_payment"]:
                platform = st.selectbox(
                    translations[st.session_state.language]["online_method"],
                    ["JazzCash", "EasyPaisa", "SadaPay", "NayaPay", "YouPaisa", "Bank Transfer"],
                    key="online_method"
                )

                if platform in ["JazzCash", "EasyPaisa", "SadaPay", "NayaPay", "YouPaisa"]:
                    phone = st.text_input(f"Enter your {platform} number (e.g., 03XXXXXXXXX)", max_chars=11)
                    if not phone.startswith("03") or len(phone) != 11:
                        valid_payment = False
                        st.warning("⚠️ Please enter a valid 11-digit mobile number")

                elif platform == "Bank Transfer":
                    bank = st.selectbox("Select Your Bank", [
                        "Meezan Bank", "UBL", "HBL", "Allied Bank", "Faysal Bank", "MCB", "Bank Alfalah", "Askari Bank", "Other"
                    ], key="bank_selection")

                    account_number = st.text_input(f"Enter your {bank} Account Number", max_chars=16)
                    if len(account_number) < 10:
                        valid_payment = False
                        st.warning("⚠️ Please enter a valid bank account number (at least 10 digits)")

            if payment_type == translations[st.session_state.language]["cash_on_delivery"] or (payment_type == translations[st.session_state.language]["online_payment"] and st.session_state.otp_verified):
                if st.button(translations[st.session_state.language]["confirm_payment"]):
                    from src.order_utils import save_order_to_csv, generate_invoice_pdf

                    if payment_type == translations[st.session_state.language]["cash_on_delivery"]:
                        save_order_to_csv(st.session_state.cart, products)
                        generate_invoice_pdf(st.session_state.cart, products)
                        with open("invoice.pdf", "rb") as f:
                            st.download_button("📄 Download Invoice", f, file_name="invoice.pdf")

                        st.success("✅ Order placed with Cash on Delivery!")
                        st.balloons()
                        st.session_state.cart = {}
                        st.session_state.checkout = False

                    elif payment_type == translations[st.session_state.language]["online_payment"]:
                        if valid_payment:
                            save_order_to_csv(st.session_state.cart, products)
                            generate_invoice_pdf(st.session_state.cart, products)
                            with open("invoice.pdf", "rb") as f:
                                st.download_button("📄 Download Invoice", f, file_name="invoice.pdf")

                            st.success(f"✅ Payment received via {platform if platform != 'Bank Transfer' else bank}!")
                            st.balloons()
                            st.session_state.cart = {}
                            st.session_state.checkout = False
                        else:
                            st.error("❌ Please complete all online payment fields correctly.")
            elif payment_type == translations[st.session_state.language]["online_payment"] and not st.session_state.otp_verified:
                if not st.session_state.otp_sent:
                    if st.button(translations[st.session_state.language]["send_otp"]):
                        import random
                        st.session_state.generated_otp = str(random.randint(100000, 999999))
                        st.session_state.otp_sent = True
                        st.info(
                            f"🔐 OTP sent to your {platform if platform != 'Bank Transfer' else bank} number/account! (Simulated OTP: {st.session_state.generated_otp})"
                        )

                if st.session_state.otp_sent and not st.session_state.otp_verified:
                    user_otp = st.text_input("Enter the 6-digit OTP sent to you:", max_chars=6)
                    if st.button(translations[st.session_state.language]["verify_otp"]):
                        if user_otp == st.session_state.generated_otp:
                            st.session_state.otp_verified = True
                            st.success("✅ OTP Verified!")
                            st.rerun()
                        else:
                            st.error("❌ Incorrect OTP. Please try again.")
        else:
            st.warning("🛒 Your cart is empty. Please add items before proceeding to checkout.")

    # File uploader
    uploaded_file = st.file_uploader(translations[st.session_state.language]["upload_image"], type=["jpg", "jpeg", "png", "jfif"])

    if uploaded_file:
        if uploaded_file.type.startswith("image/"):
            st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
            image = Image.open(uploaded_file).convert("RGB")
            image_input = preprocess(image).unsqueeze(0).to(device)

            product_names = [product["name"] for product in products.values()]
            text_inputs = clip.tokenize(product_names).to(device)

            with torch.no_grad():
                image_features = clip_model.encode_image(image_input)
                text_features = clip_model.encode_text(text_inputs)

                image_features /= image_features.norm(dim=-1, keepdim=True)
                text_features /= text_features.norm(dim=-1, keepdim=True)
                similarity = (image_features @ text_features.T).squeeze()

                best_idx = similarity.argmax().item()
                predicted_name = product_names[best_idx]
                st.success(f"{translations[st.session_state.language]['closest_match']}: {predicted_name}")

                predicted_key = predicted_name.split()[0].lower().strip()
                if predicted_key not in products:
                    product_keys = list(products.keys())
                    for key in product_keys:
                        if predicted_key in key.lower() or key.lower() in predicted_name.lower():
                            predicted_key = key.lower()
                            break

                if predicted_key in products:
                    current_key = st.session_state.get("last_product_key")
                    if not current_key or predicted_key != current_key:
                        st.session_state.query = predicted_key
                        st.session_state.last_product_key = predicted_key
                        gemini_response = gemini_model.generate_content(
                            f"Write a short 4-5 line description about the product {predicted_key} in 50 words only"
                        )
                        st.session_state.last_product_description = gemini_response.text
                        st.rerun()
                else:
                    st.warning(translations[st.session_state.language]["not_found"])

st.markdown("---")
st.write("Developed by Ai Engineer Mujahid Kareem | © 2025")