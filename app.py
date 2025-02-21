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
# Initialize watchlist in session state
if "watchlist" not in st.session_state:
    st.session_state.watchlist = []

# Function to get stock data
def get_stock_data(symbol):
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period='1d')
        if not data.empty:
            return {
                'Last Price': data['Close'].iloc[-1],
                'Open': data['Open'].iloc[-1],
                'High': data['High'].iloc[-1],
                'Low': data['Low'].iloc[-1],
                'Volume': data['Volume'].iloc[-1]
            }
        return None
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {str(e)}")
        return None

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
        options=["MoneyMaven Pro", "Stock Dashboard", "ChatBot", "VisionBot"],
        icons=["house", "graph-up", "robot", "eye"],
        default_index=0,
        orientation="vertical",
    )
# Welcome Section
if selected == "MoneyMaven Pro":
    st.title("Money Maven Pro")
    st.subheader("Your Professional Market Intelligence Platform")
    
    # Overview Section
    st.markdown("""
    Access real-time market data, AI-powered analysis, and advanced visualization tools 
    in one comprehensive platform.
    """)
    
    # Main Features in Three Columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### Market Dashboard")
        st.markdown("""
        Everything you need for market analysis:
        - Real-time market data
        - Custom watchlists
        - Technical indicators
        - Financial statements
        - Latest market news
        """)
        if st.button("Open Dashboard"):
            st.session_state.selected_option = "Stock Dashboard"
            st.rerun()
            
    with col2:
        st.markdown("### Market Intelligence AI")
        st.markdown("""
        Your personal market analyst:
        - Market insights
        - Company analysis
        - Strategy validation
        - Risk assessment
        - Trend analysis
        """)
        if st.button("Access AI Analyst"):
            st.session_state.selected_option = "ChatBot"
            st.rerun()
            
    with col3:
        st.markdown("### Technical Analysis")
        st.markdown("""
        Advanced chart analysis:
        - Pattern recognition
        - Technical indicators
        - Trend analysis
        - Chart interpretation
        - Market signals
        """)
        if st.button("Analyze Charts"):
            st.session_state.selected_option = "VisionBot"
            st.rerun()
    
    # Key Features
    st.markdown("### Platform Capabilities")
    
    tab1, tab2, tab3 = st.tabs(["Market Analysis", "AI Insights", "Technical Tools"])
    
    with tab1:
        st.markdown("""
        **Market Analysis Suite**
        - Real-time price monitoring
        - Custom watchlist management
        - Financial statement analysis
        - Key performance metrics
        - Market news integration
        """)
        
    with tab2:
        st.markdown("""
        **AI-Powered Insights**
        - Market sentiment analysis
        - Investment strategy validation
        - Risk assessment tools
        - Performance forecasting
        - Pattern recognition
        """)
        
    with tab3:
        st.markdown("""
        **Technical Analysis Tools**
        - Advanced chart analysis
        - Technical indicator suite
        - Pattern identification
        - Trend analysis
        - Visual market intelligence
        """)
    
    # Quick Start Section
    st.markdown("### Getting Started")
    with st.expander("Platform Guide"):
        st.markdown("""
        **Market Dashboard:**
        - Add securities to your watchlist
        - Access fundamental data
        - Monitor real-time market movements
        
        **AI Analysis:**
        - Query market conditions
        - Validate investment hypotheses
        - Get real-time market insights
        
        **Technical Analysis:**
        - Upload charts for analysis
        - Identify patterns and trends
        - Get professional interpretations
        """)
    
    # Market Insights Section
    st.markdown("### Professional Tools")
    with st.expander("Available Features"):
        st.markdown("""
        **Analysis Tools:**
        - Real-time market data
        - Technical indicators
        - Financial metrics
        - News integration
        
        **Risk Management:**
        - Portfolio analysis
        - Market risk assessment
        - Performance tracking
        
        **Market Intelligence:**
        - AI-driven insights
        - Pattern recognition
        - Trend analysis
        """)
    
    # Support Section
    st.markdown("### Support")
    with st.expander("Help Center"):
        st.markdown("""
        **Need assistance?**
        - Verify your market data feed
        - Check security identifiers
        - Refresh for real-time updates
        - Contact support for technical issues
        """)
        
    # Disclaimer at the bottom
    st.markdown("""
    ---
    *Market data delayed by 15 minutes unless specified. Analysis tools are for informational purposes only.*
    """)

# Stock Dashboard Section
if selected == "Stock Dashboard":
    st.title('📈 Stock Dashboard')
    
    # Add stock to watchlist
    col1, col2 = st.columns([2, 1])
    
    with col1:
        new_stock = st.text_input("Enter stock symbol (e.g., AAPL, GOOGL)", key="stock_input")
    
    with col2:
        if st.button("Add to Watchlist"):
            if new_stock:
                if new_stock not in st.session_state.watchlist:
                    st.session_state.watchlist.append(new_stock.upper())
                    st.success(f"Added {new_stock.upper()} to watchlist!")
                else:
                    st.warning("Stock already in watchlist!")
    
    # Display watchlist
    if st.session_state.watchlist:
        st.subheader("Your Watchlist")
        
        # Create a container for the watchlist table
        watchlist_container = st.container()
        
        # Create columns for the table header
        cols = watchlist_container.columns([1, 1, 1, 1, 1, 1, 1])
        headers = ["Symbol", "Last Price", "Open", "High", "Low", "Volume", "Action"]
        
        for col, header in zip(cols, headers):
            col.markdown(f"**{header}**")
        
        # Display stock data
        for symbol in st.session_state.watchlist:
            stock_data = get_stock_data(symbol)
            
            if stock_data:
                cols = watchlist_container.columns([1, 1, 1, 1, 1, 1, 1])
                cols[0].write(symbol)
                cols[1].write(f"${stock_data['Last Price']:.2f}")
                cols[2].write(f"${stock_data['Open']:.2f}")
                cols[3].write(f"${stock_data['High']:.2f}")
                cols[4].write(f"${stock_data['Low']:.2f}")
                cols[5].write(f"{stock_data['Volume']:,.0f}")
                
                if cols[6].button("Remove", key=f"remove_{symbol}"):
                    st.session_state.watchlist.remove(symbol)
                    st.rerun()
    
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
