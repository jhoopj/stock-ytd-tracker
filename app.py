import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

# Page setup - optimized for desktop and mobile viewports
st.set_page_config(
    page_title="HOOPES Stock YTD Tracker", 
    page_icon="📈",
    layout="wide"
)

st.title("📈 Stock Watchlist - YTD Tracker")

# 1. Ticker Input Section
default_tickers = "AAPL, NVDA, MSFT, GOOG, AMZN"
ticker_input = st.text_input(
    "Enter Stock Tickers (comma separated):", 
    value=default_tickers
)

tickers = [t.strip().upper() for t in ticker_input.split(",") if t.strip()]

if tickers:
    @st.cache_data(ttl=3600)  # Cache data for 1 hour to reduce load times
    def get_ytd_data(ticker_list):
        try:
            data = yf.download(ticker_list, period="ytd", progress=False)["Close"]
            if isinstance(data, pd.Series):
                data = data.to_frame(name=ticker_list[0])
            return data
        except Exception as e:
            st.error(f"Error fetching data: {e}")
            return pd.DataFrame()

    with st.spinner("Fetching stock prices..."):
        ytd_df = get_ytd_data(tickers)

    if not ytd_df.empty:
        # Create tabs for clean mobile navigation
        tab1, tab2 = st.tabs(["📊 YTD % Comparison", "💵 Single Stock Price"])

        with tab1:
            st.subheader("Normalized YTD % Growth")
            
            # Calculate % change from start of year
            ytd_pct = (ytd_df / ytd_df.iloc[0] - 1) * 100

            fig_pct = go.Figure()
            for col in ytd_pct.columns:
                fig_pct.add_trace(go.Scatter(
                    x=ytd_pct.index, 
                    y=ytd_pct[col], 
                    mode='lines', 
                    name=col
                ))
            
            fig_pct.update_layout(
                xaxis_title="Date",
                yaxis_title="YTD Gain / Loss (%)",
                hovermode="x unified",
                template="plotly_dark",
                height=450,
                margin=dict(l=10, r=10, t=30, b=10),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_pct, use_container_width=True)

        with tab2:
            st.subheader("Historical Closing Price ($)")
            selected_ticker = st.selectbox("Select Ticker:", tickers)
            
            if selected_ticker in ytd_df.columns and not ytd_df[selected_ticker].dropna().empty:
                clean_series = ytd_df[selected_ticker].dropna()
                
                # Metric Calculations
                start_price = clean_series.iloc[0]
                latest_price = clean_series.iloc[-1]
                prev_close = clean_series.iloc[-2] if len(clean_series) > 1 else start_price
                
                # YTD % Change
                ytd_pct_change = ((latest_price - start_price) / start_price) * 100
                
                # Daily Change ($ and %)
                daily_change_dollar = latest_price - prev_close
                daily_change_pct = (daily_change_dollar / prev_close) * 100
                
                # Metric Cards - Daily Change and YTD Return in the same row
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Current Price", f"${latest_price:.2f}")
                col2.metric(
                    "1-Day Change", 
                    f"${daily_change_dollar:+.2f}", 
                    delta=f"{daily_change_pct:+.2f}%"
                )
                col3.metric(
                    "YTD Return", 
                    f"{ytd_pct_change:+.2f}%", 
                    delta=f"{ytd_pct_change:+.2f}%"
                )
                col4.metric("Start Price (Jan 1)", f"${start_price:.2f}")

                fig_stock = go.Figure()
                fig_stock.add_trace(go.Scatter(
                    x=clean_series.index, 
                    y=clean_series, 
                    mode='lines', 
                    name=selected_ticker,
                    line=dict(color='#00CC96', width=2)
                ))

                fig_stock.update_layout(
                    title=f"{selected_ticker} YTD Price Action",
                    xaxis_title="Date",
                    yaxis_title="Price ($)",
                    hovermode="x unified",
                    template="plotly_dark",
                    height=400,
                    margin=dict(l=10, r=10, t=40, b=10)
                )
                st.plotly_chart(fig_stock, use_container_width=True)
            else:
                st.warning(f"No price data available for {selected_ticker}.")
    else:
        st.error("Could not retrieve stock data. Please check ticker symbols.")
