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
st.set_page_config(page_title="Finance & Health Assistant", page_icon="🤖", layout="wide")

# Initialize API keys
alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')
marketaux_api_key = os.getenv('MARKETAUX_API_KEY')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# Configure Gemini
gen_ai.configure(api_key=GOOGLE_API_KEY)

# Safety settings for Gemini
safety_settings = [
    {"category": "HARM_CATEGORY_DANGEROUS", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

# Helper functions
def translate_role_for_streamlit(user_role):
    return "assistant" if user_role == "model" else user_role

def image_to_byte_array(image: Image) -> bytes:
    imgByteArr = io.BytesIO()
    image.save(imgByteArr, format=image.format)
    return imgByteArr.getvalue()

# Main navigation
with st.sidebar:
    selected = option_menu(
        menu_title="Finance & Health",
        options=["Stock Dashboard", "VisionBot"],
        icons=["graph-up", "robot", "eye"],
        default_index=0,
        orientation="vertical",
    )

# Stock Dashboard Section
if selected == "Stock Dashboard":
    st.title('Stock Market Dashboard')
    
    # Sidebar inputs for stock analysis
    ticker = st.sidebar.text_input('Ticker', value='AAPL')
    start_date = st.sidebar.date_input('Start Date')
    end_date = st.sidebar.date_input('End Date')

    if ticker and start_date and end_date:
        try:
            data = yf.download(ticker, start=start_date, end=end_date)
            
            if not data.empty:
                if isinstance(data.columns, pd.MultiIndex):
                    data = data['Adj Close'] if 'Adj Close' in data.columns else data['Close']
                else:
                    data = data[['Adj Close']] if 'Adj Close' in data.columns else data[['Close']]
                
                data.rename(columns={data.columns[0]: "Price"}, inplace=True)
                
                fig = px.line(data, x=data.index, y="Price", title=ticker)
                st.plotly_chart(fig)

                # Tabs for different data views
                pricing_data, fundamental_data, news = st.tabs(["Pricing Data", "Fundamental Data", "Top 10 News"])
                
                with pricing_data:
                    st.header("Price Movements")
                    data['% Change'] = data['Price'].pct_change()
                    data.dropna(inplace=True)
                    st.write(data)
                    
                    annual_return = data['% Change'].mean() * 252 * 100
                    stdev = np.std(data['% Change']) * np.sqrt(252) * 100
                    risk_adj_return = annual_return / stdev if stdev != 0 else 0
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Annual Return", f"{annual_return:.2f}%")
                    with col2:
                        st.metric("Standard Deviation", f"{stdev:.2f}%")
                    with col3:
                        st.metric("Risk-Adjusted Return", f"{risk_adj_return:.2f}")

                with fundamental_data:
                    if alpha_vantage_key:
                        fd = FundamentalData(alpha_vantage_key, output_format='pandas')
                        try:
                            for statement, title in [
                                (fd.get_balance_sheet_annual, "Balance Sheet"),
                                (fd.get_income_statement_annual, "Income Statement"),
                                (fd.get_cash_flow_annual, "Cash Flow Statement")
                            ]:
                                st.subheader(title)
                                data = statement(ticker)[0]
                                df = data.T[2:]
                                df.columns = list(data.T.iloc[0])
                                st.write(df)
                        except Exception as e:
                            st.error(f"Error fetching fundamental data: {e}")
                    else:
                        st.warning("Alpha Vantage API key is missing")

                with news:
                    st.header(f'📰 Latest News for {ticker}')
                    if marketaux_api_key:
                        try:
                            conn = http.client.HTTPSConnection('api.marketaux.com')
                            params = urllib.parse.urlencode({
                                'api_token': marketaux_api_key,
                                'symbols': ticker,
                                'limit': 10,
                            })
                            conn.request('GET', f'/v1/news/all?{params}')
                            news_data = json.loads(conn.getresponse().read().decode('utf-8'))
                            
                            if 'data' in news_data:
                                for i, article in enumerate(news_data['data'][:10]):
                                    with st.expander(f"📰 {article['title']}"):
                                        st.write(f"Published: {article['published_at']}")
                                        st.write(f"Summary: {article['description']}")
                                        st.markdown(f"[Read More]({article['url']})")
                            else:
                                st.warning("No news found")
                        except Exception as e:
                            st.error(f"Error fetching news: {e}")
                    else:
                        st.warning("MarketAux API key is missing")
            else:
                st.error("No data found for this ticker")
        except Exception as e:
            st.error(f"Error: {e}")

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
                        [image_prompt, image],
                        safety_settings=safety_settings
                    )
                    st.markdown("### Analysis")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Error analyzing image: {e}")
            else:
                st.warning("Please provide a prompt for the image analysis")
