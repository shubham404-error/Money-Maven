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

# Stock Dashboard Section
if selected == "Stock Dashboard":
    st.title('📈 Stock Dashboard')
    st.link_button("🔗 Open Full Stock Dashboard", "https://stocks-dashboard-404.streamlit.app/")

    
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
    st.title("VisionBot Analysis")
    uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg", "webp"])
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, use_column_width=True)
