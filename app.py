import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import http.client
import os
import urllib.parse
import json
from alpha_vantage.fundamentaldata import FundamentalData
from dotenv import load_dotenv
import google.generativeai as gen_ai
from PIL import Image
from datetime import date
from streamlit_option_menu import option_menu

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(page_title="Money Maven Pro", page_icon="🤖", layout="wide")
st.image("logo.png", width=100)

# Initialize API keys
alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')
marketaux_api_key = os.getenv('MARKETAUX_API_KEY')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# Set up Google Gemini-Pro AI model
gen_ai.configure(api_key=GOOGLE_API_KEY)
model = gen_ai.GenerativeModel('gemini-pro')

# Initialize chat session in Streamlit if not already present
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# Safety settings for Gemini
safety_settings = [
    {"category": "HARM_CATEGORY_DANGEROUS", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

# Main navigation
with st.sidebar:
    selected = option_menu(
        menu_title="Finance",
        options=["Stock Dashboard", "ChatBot", "VisionBot"],
        icons=["graph-up", "robot", "eye"],
        default_index=0,
        orientation="vertical",
    )
# Initialize watchlist in session state
if "watchlist" not in st.session_state:
    st.session_state.watchlist = []

# Stock Dashboard Section
if selected == "Stock Dashboard":
    st.title('📈 Stock Dashboard')
    st.link_button("🔗 Open Full Stock Dashboard", "https://stocks-dashboard-404.streamlit.app/")
        # Add stock to watchlist
    ticker = st.text_input("Enter stock ticker (e.g., AAPL, TSLA):")
    if st.button("Add to Watchlist") and ticker:
        if ticker.upper() not in st.session_state.watchlist:
            st.session_state.watchlist.append(ticker.upper())
            st.success(f"{ticker.upper()} added to watchlist!")
        else:
            st.warning("Stock already in watchlist.")

    # Display watchlist
    if st.session_state.watchlist:
        st.subheader("📋 Your Watchlist")
        watchlist_data = []
        for stock in st.session_state.watchlist:
            try:
                stock_data = yf.Ticker(stock).history(period="1d")
                if not stock_data.empty:
                    last_price = stock_data["Close"].iloc[-1]
                    open_price = stock_data["Open"].iloc[-1]
                    high_price = stock_data["High"].iloc[-1]
                    low_price = stock_data["Low"].iloc[-1]
                    volume = stock_data["Volume"].iloc[-1]
                    watchlist_data.append({
                        "Stock": stock,
                        "Open": open_price,
                        "High": high_price,
                        "Low": low_price,
                        "Close": last_price,
                        "LTP": last_price,
                        "Volume": volume
                    })
                else:
                    watchlist_data.append({"Stock": stock, "Open": "N/A", "High": "N/A", "Low": "N/A", "Close": "N/A", "LTP": "N/A", "Volume": "N/A"})
            except:
                watchlist_data.append({"Stock": stock, "Open": "Error", "High": "Error", "Low": "Error", "Close": "Error", "LTP": "Error", "Volume": "Error"})
        
        df = pd.DataFrame(watchlist_data)
        st.dataframe(df)

    # Remove stock from watchlist
    remove_ticker = st.selectbox("Remove stock from watchlist:", ["Select"] + st.session_state.watchlist)
    if remove_ticker != "Select" and st.button("Remove"):
        st.session_state.watchlist.remove(remove_ticker)
        st.success(f"{remove_ticker} removed from watchlist.")

    
# ChatBot Section
elif selected == "ChatBot":
    st.title("Chat with Money Maven Bot™")
    user_prompt = st.chat_input("Ask DocBot...")
    if user_prompt:
        st.chat_message("user").markdown(user_prompt)
        response = st.session_state.chat_session.send_message(user_prompt, safety_settings=safety_settings)
        st.chat_message("assistant").markdown(response.text)

# VisionBot Section
elif selected == "VisionBot":
    st.header("👁 Visionbot™")
    st.write("")

    image_prompt = st.text_input("Interact with the Image", placeholder="Prompt", label_visibility="visible")
    uploaded_file = st.file_uploader("Choose an Image", accept_multiple_files=False, type=["png", "jpg", "jpeg", "img", "webp"])

    if uploaded_file is not None:
        st.image(Image.open(uploaded_file), use_column_width=True)
        st.markdown("""
            <style>
            img {
                border-radius: 10px;
            }
            </style>
        """, unsafe_allow_html=True)

    if st.button("GET RESPONSE", use_container_width=True):
        # Update model name to gemini-1.5-flash
        model = gen_ai.GenerativeModel("gemini-1.5-flash")
        
        if uploaded_file is not None:
            if image_prompt != "":
                image = Image.open(uploaded_file)
                
                # Simplified content creation
                response = model.generate_content(
                    [
                        image_prompt,
                        image
                    ],
                    safety_settings=safety_settings
                )
                
                st.write("")
                st.write(":blue[Response]")
                st.write("")
                st.markdown(response.text)
            else:
                st.write("")
                st.header(":red[Please Provide a prompt]")
        else:
            st.write("")
            st.header(":red[Please Provide an image]")
