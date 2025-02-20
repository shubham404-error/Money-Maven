import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import http.client
import urllib.parse
import json
from dotenv import load_dotenv
import os

# Load API key from environment file
load_dotenv()
MARKETAUX_API_KEY = os.getenv("MARKETAUX_API_KEY")

st.title('Ritvik Streamlit Stock Dashboard')

ticker = st.sidebar.text_input('Ticker')
start_date = st.sidebar.date_input('Start Date')
end_date = st.sidebar.date_input('End Date')

data = yf.download(ticker,start=start_date, end=end_date)

fig = px.line(data, x = data.index, y = data['Adj Close'], title = ticker)
st.plotly_chart(fig)

pricing_data, fundamental_data, news = st.tabs(["Pricing Data", "Fundamental Data", "Top 10 News"])

with pricing_data:
   st.header("Price Movements")
   data2 = data
   data2['% Change'] = data2['Adj Close']/data2['Adj Close'].shift(1) - 1
   data2.dropna(inplace = True)
   st.write(data2)
   annual_return = data2['% Change'].mean()*252*100
   st.write('Annual Return is ',annual_return,'%')
   stdev = np.std(data2['% Change'])*np.sqrt(252)
   st.write('Standard Deviation is ',stdev*100,'%')
   st.write('Risk Adj. Return is ',annual_return/(stdev*100))

from alpha_vantage.fundamentaldata import FundamentalData   
with fundamental_data:
   key = 'OW1639L63B5UCYYL'
   fd = FundamentalData(key,output_format = 'pandas')
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

with news:
    st.header(f'News of {ticker}')
    conn = http.client.HTTPSConnection('api.marketaux.com')
    params = urllib.parse.urlencode({
        'api_token': MARKETAUX_API_KEY,
        'symbols': ticker,
        'limit': 10,
    })
    conn.request('GET', f'/v1/news/all?{params}')
    res = conn.getresponse()
    data = json.loads(res.read().decode('utf-8'))
    
    if 'data' in data:
        for i, article in enumerate(data['data'][:10]):
            st.subheader(f'News {i+1}')
            st.write(article['published_at'])
            st.write(article['title'])
            st.write(article['description'])
            st.write(f"Source: {article['source']} - [Read More]({article['url']})")
    else:
        st.write("No news available.")