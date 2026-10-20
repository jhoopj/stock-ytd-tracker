import pandas as pd
import yfinance as yf
import streamlit as st


def get_stock_data(ticker_symbol):
  ticker = yf.Ticker(ticker_symbol)

  # Fetch 1 year of daily historical data to cover YTD and 30-day calculations
  hist = ticker.history(period="1y")

  if hist.empty:
    return None

  # Current price and previous close
  current_price = hist["Close"].iloc[-1]
  prev_close = hist["Close"].iloc[-2] if len(hist) > 1 else current_price

  # Daily change (%)
  daily_change = ((current_price - prev_close) / prev_close) * 100

  # 30-day change (%)
  # Uses the price from 30 calendar days/sessions ago (or earliest available)
  price_30d_ago = hist["Close"].iloc[-30] if len(hist) >= 30 else hist["Close"].iloc[0]
  change_30d = ((current_price - price_30d_ago) / price_30d_ago) * 100

  # Year-To-Date (YTD) change (%)
  current_year = pd.Timestamp.now().year
  ytd_data = hist[hist.index.year == current_year]

  if not ytd_data.empty:
    start_of_year_price = ytd_data["Close"].iloc[0]
    ytd_change = (
        (current_price - start_of_year_price) / start_of_year_price
    ) * 100
  else:
    ytd_change = 0.0

  return {
      "Current Price": current_price,
      "Daily Change (%)": daily_change,
      "30-Day Change (%)": change_30d,
      "YTD Change (%)": ytd_change,
  }


# Streamlit UI
st.title("Stock YTD & Daily Tracker")

ticker_input = st.text_input("Enter Stock Ticker (e.g., AAPL, MSFT):", "AAPL")

if ticker_input:
  data = get_stock_data(ticker_input)

  if data:
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Current Price", f"${data['Current Price']:.2f}")
    col2.metric("Daily Change", f"{data['Daily Change (%)']:.2f}%")
    col3.metric("30-Day Change", f"{data['30-Day Change (%)']:.2f}%")
    col4.metric("YTD Change", f"{data['YTD Change (%)']:.2f}%")
  else:
    st.error("Invalid ticker symbol or no data available.")
