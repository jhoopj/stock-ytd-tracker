import pandas as pd
import streamlit as st
import yfinance as yf


def get_portfolio_data(ticker_list):
  results = []

  for ticker_symbol in ticker_list:
    ticker_symbol = str(ticker_symbol).strip().upper()
    if not ticker_symbol or ticker_symbol == "NAN":
      continue

    ticker = yf.Ticker(ticker_symbol)
    hist = ticker.history(period="1y")

    if hist.empty:
      continue

    current_price = hist["Close"].iloc[-1]
    prev_close = hist["Close"].iloc[-2] if len(hist) > 1 else current_price

    daily_change = ((current_price - prev_close) / prev_close) * 100

    price_30d_ago = (
        hist["Close"].iloc[-30] if len(hist) >= 30 else hist["Close"].iloc[0]
    )
    change_30d = ((current_price - price_30d_ago) / price_30d_ago) * 100

    current_year = pd.Timestamp.now().year
    ytd_data = hist[hist.index.year == current_year]

    if not ytd_data.empty:
      start_of_year_price = ytd_data["Close"].iloc[0]
      ytd_change = (
          (current_price - start_of_year_price) / start_of_year_price
      ) * 100
    else:
      ytd_change = 0.0

    results.append({
        "Ticker": ticker_symbol,
        "Price ($)": round(current_price, 2),
        "Daily Change (%)": round(daily_change, 2),
        "30-Day Change (%)": round(change_30d, 2),
        "YTD Change (%)": round(ytd_change, 2),
    })

  return pd.DataFrame(results)


# Streamlit UI
st.set_page_config(layout="wide")
st.title("Stock Portfolio & Watchlist Tracker")

DEFAULT_WATCHLIST = (
    "LUNR, CAT, POOL, BLOK, SI=F, NMAX, JEF, RKLB, PLD, NEE, KMI, O, COIN,"
    " FRSH, SYF, VSAT, HIMS, MELI, GME, BA, LEN, FBTC.TO, APLD, SGML, BROS,"
    " CELH, LOW, HD, UUUU, KLIC, VICI, DKNG, AVGE, ACLS, CARR, INTU, BUR, DRV,"
    " ALB, DHR, TMUS, CPRT, AVGO, ORCL, ULTA, BAC, AMPX, ENPH, F, NLST, SHW,"
    " TXN, VZ, TMC, LUV, RSI, NOW, EDUC, PM, STLJF, BIP, ABCL, LMT, TSCDY, ANDE,"
    " SH, SEF, QQJG, CIBR, ONEQ, FLNA, 9031.T, ^DJUSRR, YXI, CRSP, CWCO"
)

tab1, tab2 = st.tabs(["Saved Watchlist", "Upload CSV File"])

tickers = []

with tab1:
  user_input = st.text_area(
      "Ticker Symbols:", DEFAULT_WATCHLIST, height=120
  )
  if user_input:
    tickers = [t.strip() for t in user_input.split(",") if t.strip()]

with tab2:
  uploaded_file = st.file_uploader(
      "Upload Yahoo Finance CSV", type=["csv"]
  )
  if uploaded_file is not None:
    uploaded_df = pd.read_csv(uploaded_file)
    symbol_col = [
        col
        for col in uploaded_df.columns
        if col.lower() in ["symbol", "ticker", "tickers"]
    ]
    if symbol_col:
      tickers = uploaded_df[symbol_col[0]].dropna().astype(str).tolist()

if tickers:
  with st.spinner(f"Fetching market data for {len(tickers)} symbols..."):
    df = get_portfolio_data(tickers)

  if not df.empty:
    # 1. Summary Metrics Displayed in Columns
    st.subheader("Portfolio Summary Breakdown")
    col1, col2, col3, col4 = st.columns(4)

    avg_daily = df["Daily Change (%)"].mean()
    avg_30d = df["30-Day Change (%)"].mean()
    avg_ytd = df["YTD Change (%)"].mean()
    total_tracked = len(df)

    col1.metric("Total Stocks Tracked", total_tracked)
    col2.metric("Avg Daily Change", f"{avg_daily:+.2f}%")
    col3.metric("Avg 30-Day Change", f"{avg_30d:+.2f}%")
    col4.metric("Avg YTD Change", f"{avg_ytd:+.2f}%")

    st.markdown("---")

    # 2. Main Stock Table Breakdown
    st.subheader("All Tracked Holdings")
    st.dataframe(
        df.style.format({
            "Price ($)": "${:.2f}",
            "Daily Change (%)": "{:+.2f}%",
            "30-Day Change (%)": "{:+.2f}%",
            "YTD Change (%)": "{:+.2f}%",
        }),
        use_container_width=True,
    )

    st.markdown("---")

    # 3. Top Seven Performing Stocks Section
    st.subheader("Top 7 Performing Stocks (YTD)")
    top_7_df = df.nlargest(7, "YTD Change (%)").reset_index(drop=True)

    top_cols = st.columns(7)
    for idx, row in top_7_df.iterrows():
      with top_cols[idx]:
        st.metric(
            label=row["Ticker"],
            value=f"${row['Price ($)']:.2f}",
            delta=f"{row['YTD Change (%)']:+.2f}% YTD",
        )

    st.dataframe(
        top_7_df.style.format({
            "Price ($)": "${:.2f}",
            "Daily Change (%)": "{:+.2f}%",
            "30-Day Change (%)": "{:+.2f}%",
            "YTD Change (%)": "{:+.2f}%",
        }),
        use_container_width=True,
    )
