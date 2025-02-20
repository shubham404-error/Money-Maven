import streamlit as st
import pandas as pd
import yfinance as yf
import os
from dotenv import load_dotenv
from streamlit_option_menu import option_menu

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(page_title="Money Maven Pro", page_icon="🤖", layout="wide")
st.image("logo.png", width=100)

# Initialize API keys
alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')
marketaux_api_key = os.getenv('MARKETAUX_API_KEY')

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
                last_price = stock_data["Close"].iloc[-1] if not stock_data.empty else "N/A"
                watchlist_data.append({"Stock": stock, "Last Traded Price": last_price})
            except:
                watchlist_data.append({"Stock": stock, "Last Traded Price": "Error fetching data"})
        
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
        response = "This is a placeholder response from the chatbot."
        st.chat_message("assistant").markdown(response)

# VisionBot Section
elif selected == "VisionBot":
    st.title("VisionBot Analysis")
    uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg", "webp"])
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, use_column_width=True)
