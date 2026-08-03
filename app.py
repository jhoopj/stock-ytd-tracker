import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

# Page setup
st.set_page_config(page_title="HOOPES Stock Watchlist - YTD & Daily Tracker", layout="wide", page_icon="📈")

st.title("📈 HOOPES Stock Watchlist - YTD & Daily Performance")
st.write("Track live prices, daily gains/losses, and Year-To-Date (YTD) percent returns.")

# Sidebar for Ticker Input
st.sidebar.header("Watchlist Controls")
default_tickers = ["NVDA", "AAPL", "MSFT", "GOOG", "AMZN", "TSLA"]

user_tickers = st.sidebar.text_input(
    "Enter Stock Tickers (comma-separated):",
    value=", ".join(default_tickers)
)

# Process Tickers
tickers = [t.strip().upper() for t in user_tickers.split(",") if t.strip()]

if not tickers:
    st.warning("Please enter at least one valid ticker symbol.")
    st.stop()

# Fetch YTD & Daily Data
@st.cache_data(ttl=900)  # Refresh every 15 minutes for closer-to-real-time daily stats
def get_ytd_data(ticker_list):
    try:
        # Fetch YTD historical data
        data = yf.download(ticker_list, period="ytd", interval="1d")["Close"]
        
        # Handle single ticker return shape
        if isinstance(data, pd.Series):
            data = data.to_frame(name=ticker_list[0])
            
        return data
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

with st.spinner("Fetching market data..."):
    df_close = get_ytd_data(tickers)

if df_close.empty:
    st.error("No data retrieved. Please verify your ticker symbols.")
    st.stop()

# Drop columns that failed to return data
df_close = df_close.dropna(axis=1, how="all")

if df_close.empty:
    st.error("Could not load price data for the specified tickers.")
    st.stop()

# Calculate YTD % Return relative to first trading day of the year
first_valid_prices = df_close.bfill().iloc[0]
df_ytd_pct = ((df_close / first_valid_prices) - 1) * 100

# Build Summary Table Data
summary_rows = []

for ticker in tickers:
    if ticker in df_close.columns:
        price_series = df_close[ticker].dropna()
        ytd_series = df_ytd_pct[ticker].dropna()
        
        if len(price_series) >= 2:
            latest_price = price_series.iloc[-1]
            prev_price = price_series.iloc[-2]
            
            # Today's calculations
            daily_change_dollar = latest_price - prev_price
            daily_change_pct = (daily_change_dollar / prev_price) * 100
            
            # YTD calculation
            ytd_pct = ytd_series.iloc[-1]
            
            summary_rows.append({
                "Ticker": ticker,
                "Current Price": f"${latest_price:,.2f}",
                "Today's Return": f"{daily_change_dollar:+,.2f} ({daily_change_pct:+.2f}%)",
                "YTD Return": f"{ytd_pct:+.2f}%",
                "_raw_daily": daily_change_pct,  # for color styling
                "_raw_ytd": ytd_pct              # for color styling
            })

# Display Summary Table
if summary_rows:
    st.subheader("Performance Summary")
    summary_df = pd.DataFrame(summary_rows)

    # Style helper function for green/red values
    def highlight_returns(val):
        if "(" in str(val) or "%" in str(val):
            if str(val).startswith("-"):
                return "color: #ff4b4b; font-weight: bold;"  # Red for negative
            elif str(val).startswith("+"):
                return "color: #09ab3b; font-weight: bold;"  # Green for positive
        return ""

    display_df = summary_df[["Ticker", "Current Price", "Today's Return", "YTD Return"]]
    
    st.dataframe(
        display_df.style.map(highlight_returns, subset=["Today's Return", "YTD Return"]),
        use_container_width=True,
        hide_index=True
    )

# Plotly Interactive Chart
st.markdown("---")
st.subheader("YTD Percentage Return Comparison")

fig = go.Figure()

for ticker in df_ytd_pct.columns:
    clean_series = df_ytd_pct[ticker].dropna()
    if not clean_series.empty:
        fig.add_trace(go.Scatter(
            x=clean_series.index,
            y=clean_series,
            mode='lines',
            name=ticker,
            hovertemplate=f"<b>{ticker}</b><br>Date: %{{x|%b %d, %Y}}<br>YTD Return: %{{y:+.2f}}%<extra></extra>"
        ))

fig.update_layout(
    xaxis_title="Date",
    yaxis_title="YTD Return (%)",
    yaxis_ticksuffix="%",
    hovermode="x unified",
    template="plotly_white",
    height=500,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

# Zero baseline
fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.7)

st.plotly_chart(fig, use_container_width=True)
