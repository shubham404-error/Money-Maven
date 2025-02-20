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
import io
from streamlit_option_menu import option_menu

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(page_title="Money Maven Pro", page_icon="🤖", layout="wide")
st.image("logo.png",width=100)

# Initialize API keys
alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')
marketaux_api_key = os.getenv('MARKETAUX_API_KEY')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# Set up Google Gemini-Pro AI model
gen_ai.configure(api_key=GOOGLE_API_KEY)
model = gen_ai.GenerativeModel('gemini-pro')

# Function to translate roles between Gemini-Pro and Streamlit terminology
def translate_role_for_streamlit(user_role):
    if user_role == "model":
        return "assistant"
    else:
        return user_role

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
        options=["Stock Dashboard", 'ChatBot',"VisionBot"],
        icons=["graph-up", "robot", "eye"],
        default_index=0,
        orientation="vertical",
    )
    st.write(
        """
        <style>
            .css-r698ls {
                --sidebar-width: 200px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

# Stock Dashboard Section
# Stock Dashboard Section
if selected == "Stock Dashboard":
    st.title('Stock Market Dashboard')

    # Sidebar inputs for stock analysis
    ticker = st.sidebar.text_input('Ticker', value='AAPL')
    start_date = st.sidebar.date_input('Start Date')
    end_date = st.sidebar.date_input('End Date')
    if ticker and start_date and end_date:
        try:
            # Fetch Stock Data
            data = yf.download(ticker, start=start_date, end=end_date)

            if not data.empty:
                # Plot Candlestick Chart
                fig = go.Figure()
                fig.add_trace(go.Candlestick(
                    x=data.index,
                    open=data['Open'],
                    high=data['High'],
                    low=data['Low'],
                    close=data['Close'],
                    name='Candlesticks'
                ))
                fig.update_layout(title=f'{ticker} Candlestick Chart', xaxis_title='Date', yaxis_title='Price')
                st.plotly_chart(fig)
            else:
                st.error("No data found. Please check the ticker symbol and date range.")
        except Exception as e:
            st.error(f"Error fetching stock data: {e}")


    # Tabs for Different Data
    pricing_data, fundamental_data, news = st.tabs(["Pricing Data", "Fundamental Data", "Top 10 News"])

    with pricing_data:
        st.header("Price Movements")
        if not data.empty:
            data['% Change'] = data['Price'].pct_change()
            data.dropna(inplace=True)

            st.write(data)

            annual_return = data['% Change'].mean() * 252 * 100
            stdev = np.std(data['% Change']) * np.sqrt(252) * 100
            risk_adj_return = annual_return / stdev if stdev != 0 else 0

            st.write(f'📈 **Annual Return:** {annual_return:.2f}%')
            st.write(f'📊 **Standard Deviation:** {stdev:.2f}%')
            st.write(f'📉 **Risk-Adjusted Return:** {risk_adj_return:.2f}')
        else:
            st.warning("No pricing data available.")

    # Fetch Fundamental Data from Alpha Vantage
    with fundamental_data:
        if not alpha_vantage_key:
            st.warning("Alpha Vantage API key is missing. Set ALPHA_VANTAGE_API_KEY in environment variables.")
        else:
            fd = FundamentalData(alpha_vantage_key, output_format='pandas')
            try:
                st.subheader('Balance Sheet')
                balance_sheet = fd.get_balance_sheet_annual(ticker)[0]
                bs = balance_sheet.T[2:]
                bs.columns = list(balance_sheet.T.iloc[0])
                st.write(bs)

                st.subheader('Income Statement')
                income_statement = fd.get_income_statement_annual(ticker)[0]
                is1 = income_statement.T[2:]
                is1.columns = list(income_statement.T.iloc[0])
                st.write(is1)

                st.subheader('Cash Flow Statement')
                cash_flow = fd.get_cash_flow_annual(ticker)[0]
                cf = cash_flow.T[2:]
                cf.columns = list(cash_flow.T.iloc[0])
                st.write(cf)

            except Exception as e:
                st.error(f"Error fetching fundamental data: {e}")

    # Fetch News from MarketAux API
    with news:
        st.header(f'📢 Latest News for {ticker}')
        if not marketaux_api_key:
            st.warning("MarketAux API key is missing. Set MARKETAUX_API_KEY in environment variables.")
        else:
            conn = http.client.HTTPSConnection('api.marketaux.com')
            params = urllib.parse.urlencode({'api_token': marketaux_api_key, 'symbols': ticker, 'limit': 10})
            try:
                conn.request('GET', f'/v1/news/all?{params}')
                res = conn.getresponse()
                news_data = json.loads(res.read().decode('utf-8'))
                if 'data' in news_data:
                    for i, article in enumerate(news_data['data'][:10]):
                        st.subheader(f'📰 News {i+1}: {article["title"]}')
                        st.write(f'🗓 Published: {article["published_at"]}')
                        st.write(f'🔗 [Read More]({article["url"]})')
                        st.write(f'📄 Summary: {article["description"]}')
                        st.markdown("---")
                else:
                    st.warning("No news found.")
            except Exception as e:
                st.error(f"Error fetching news: {e}")

elif selected == "ChatBot":
     # Display the chatbot's title on the page
    st.title("Chat with Money Maven Bot™")

    # Display the chat history
    for message in st.session_state.chat_session.history:
        with st.chat_message(translate_role_for_streamlit(message.role)):
            st.markdown(message.parts[0].text)

    # Input field for user's message
    user_prompt = st.chat_input("Ask DocBot...")

    if user_prompt:
        # Add user's message to chat and display it
        st.chat_message("user").markdown(user_prompt)

        # Send user's message to Gemini-Pro and get the response
        
        gemini_response = st.session_state.chat_session.send_message(
        user_prompt, safety_settings=safety_settings
    )
        # Display Gemini-Pro's response
        with st.chat_message("assistant"):
            st.markdown(gemini_response.text)
# VisionBot Section
elif selected == "VisionBot":
    st.title("VisionBot Analysis")

    image_prompt = st.text_input("Describe what you'd like to analyze in the image")
    uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg", "webp"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, use_column_width=True)

        if st.button("Analyze Image", use_container_width=True):
            if image_prompt:
                model = gen_ai.GenerativeModel("gemini-1.5-flash")
                try:
                    response = model.generate_content(
                        [image_prompt, image_to_byte_array(image)],
                        safety_settings=safety_settings
                    )
                    st.markdown("### Analysis")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Error analyzing image: {e}")
            else:
                st.warning("Please provide a prompt for the image analysis")
