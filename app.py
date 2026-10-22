import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

# Page Setup
st.set_page_config(
    page_title="HOOPES Stock Watchlist - Performance Tracker",
    layout="wide",
    page_icon="📈",
)

st.title("📈 HOOPES Stock Watchlist - Portfolio Performance Tracker")
st.write(
    "Track live stock prices, Daily return, 30-Day change, and Year-To-Date"
    " (YTD) percent gains."
)

# Portfolio Categories Mapping
PORTFOLIOS = {
    "Pharma": ["NBIX", "AXSM", "PHAT"],
    "Gov ETF": ["NANC", "MAGA", "GOP"],
    "Manufacturing": [
        "SPAI",
        "UMAC",
        "PG",
        "KMB",
        "WELD",
        "IYJ",
        "XLI",
        "VIS",
        "FIDU",
    ],
    "China": [
        "WRD",
        "PONY",
        "BIDU",
        "BYDDF",
        "JD",
        "BILI",
        "KWEB",
        "FXI",
        "CQQQ",
        "NTES",
        "LI",
        "MCHI",
    ],
    "Food": [
        "FIVE",
        "TGT",
        "NGVC",
        "GIS",
        "MDLZ",
        "KHC",
        "DPZ",
        "COST",
        "TSN",
        "PEP",
        "WMT",
        "KO",
        "MCD",
    ],
    "Tech": [
        "CBRS",
        "SPCX",
        "LIN",
        "SOXQ",
        "AMZN",
        "LRCX",
        "KRKNF",
        "HII",
        "SLAB",
        "KLAR",
        "FIG",
        "BABA",
        "TTD",
        "QBTS",
        "NFLX",
        "TSM",
        "LNVGF",
        "DELL",
        "BN",
        "ASML",
        "INTC",
        "SYM",
        "SMCI",
        "ARM",
        "NET",
        "TWLO",
        "AAPL",
        "MSFT",
        "TSLA",
        "META",
        "NVDA",
        "PLTR",
        "MOD",
        "AMD",
        "SNOW",
        "GOOG",
    ],
    "BEST of US": [
        "TOYO",
        "ZETA",
        "MNTN",
        "KVYO",
        "UPSD",
        "CEG",
        "IONQ",
        "TLN",
        "D",
        "AEP",
        "GEV",
        "FIX",
        "EME",
        "PWR",
        "SBGSY",
        "ETN",
        "FN",
        "AAOI",
        "LITE",
        "COHR",
        "RBRK",
        "MARA",
        "CLS",
        "GLXY",
        "MU",
        "CCJ",
        "QXO",
        "AEHR",
        "NAGE",
        "PDYN",
        "NVTS",
        "AEE",
        "RTX",
        "V",
        "BBAI",
        "INOD",
        "SITM",
        "SOUN",
        "MRVL",
        "VRT",
        "GTLS",
        "IREN",
        "SES",
        "SPG",
        "CRDO",
        "SKYT",
    ],
    "Auto": ["LCID", "RIVN", "GM", "F"],
    "ETFs": [
        "SSPC",
        "EUAD",
        "XAR",
        "ITA",
        "FTRNX",
        "BRF",
        "POET",
        "VTSAX",
        "VYM",
        "SCHD",
        "NOBL",
        "ARKG",
        "ARKB",
        "ARKF",
        "ARKK",
        "ARKQ",
        "ARKW",
        "ARKO",
        "TLT",
        "KSA",
        "INDA",
        "INDI",
        "BRK-A",
        "BRK-B",
        "QQQ",
        "SQQQ",
        "VOO",
        "SPY",
    ],
    "Uranium": ["MP", "SRUUF", "DNN", "UUUU"],
    "Energy": ["XLE", "LNG", "OXY", "XOM", "CVX"],
    "Health": ["CVS", "JNJ", "REGN", "BSX", "ABT", "LLY", "UNH"],
    "Insurance": ["KNSL", "FNF", "MKL", "MET", "VRTX", "HRTG", "PGR", "FSCPX", "IAK"],
    "My Watchlist": [
        "LUNR",
        "CAT",
        "POOL",
        "BLOK",
        "SI=F",
        "NMAX",
        "JEF",
        "RKLB",
        "PLD",
        "NEE",
        "KMI",
        "O",
        "COIN",
        "FRSH",
        "SYF",
        "VSAT",
        "HIMS",
        "MELI",
        "GME",
        "BA",
        "LEN",
        "FBTC.TO",
        "APLD",
        "SGML",
        "BROS",
        "CELH",
        "LOW",
        "HD",
        "UUUU",
        "KLIC",
        "VICI",
        "DKNG",
        "AVGE",
        "ACLS",
        "CARR",
        "INTU",
        "BUR",
        "DRV",
        "ALB",
        "DHR",
        "TMUS",
        "CPRT",
        "AVGO",
        "ORCL",
        "ULTA",
        "BAC",
        "AMPX",
        "ENPH",
        "F",
        "NLST",
        "SHW",
        "TXN",
        "VZ",
        "TMC",
        "LUV",
        "RSI",
        "NOW",
        "EDUC",
        "PM",
        "STLJF",
        "BIP",
        "ABCL",
        "LMT",
        "TSCDY",
        "ANDE",
        "SH",
        "SEF",
        "QQJG",
        "CIBR",
        "ONEQ",
        "FLNA",
        "9031.T",
        "^DJUSRR",
        "YXI",
        "CRSP",
        "CWCO",
    ],
    "My First Portfolio": ["KKR", "BLK", "GE", "T", "JBLU", "HMC", "TM"],
}

# Sidebar Controls
st.sidebar.header("Watchlist Controls")
selected_portfolios = st.sidebar.multiselect(
    "Select Portfolios to Display:",
    options=list(PORTFOLIOS.keys()),
    default=list(PORTFOLIOS.keys()),
)

# Extract Active Tickers
active_tickers_with_category = []
for portfolio_name in selected_portfolios:
  for t in PORTFOLIOS[portfolio_name]:
    active_tickers_with_category.append((portfolio_name, t))

unique_tickers = list(
    dict.fromkeys([t[1] for t in active_tickers_with_category])
)

if not unique_tickers:
  st.warning("Please select at least one portfolio category.")
  st.stop()


# Download Market Data
@st.cache_data(ttl=900)
def fetch_stock_history(ticker_list):
  try:
    data = yf.download(ticker_list, period="1y", interval="1d")["Close"]
    if isinstance(data, pd.Series):
      data = data.to_frame(name=ticker_list[0])
    return data
  except Exception as e:
    st.error(f"Error fetching data: {e}")
    return pd.DataFrame()


with st.spinner("Downloading market data for all tickers..."):
  df_close = fetch_stock_history(unique_tickers)

if df_close.empty:
  st.error("No market data returned from Yahoo Finance.")
  st.stop()

df_close = df_close.dropna(axis=1, how="all")

# Construct Summary Table Rows
summary_rows = []
for category, ticker in active_tickers_with_category:
  if ticker in df_close.columns:
    series = df_close[ticker].dropna()
    if len(series) >= 2:
      latest_price = series.iloc[-1]
      prev_price = series.iloc[-2]

      # 1-day Change
      daily_change_pct = ((latest_price - prev_price) / prev_price) * 100

      # 30-day Change
      price_30d_ago = series.iloc[-30] if len(series) >= 30 else series.iloc[0]
      change_30d_pct = ((latest_price - price_30d_ago) / price_30d_ago) * 100

      # YTD Change
      current_year = pd.Timestamp.now().year
      ytd_series = series[series.index.year == current_year]
      if not ytd_series.empty:
        start_year_price = ytd_series.iloc[0]
        ytd_pct = ((latest_price - start_year_price) / start_year_price) * 100
      else:
        ytd_pct = 0.0

      summary_rows.append({
          "Portfolio": category,
          "Ticker": ticker,
          "Current Price": round(latest_price, 2),
          "Daily Change (%)": round(daily_change_pct, 2),
          "30-Day Change (%)": round(change_30d_pct, 2),
          "YTD Change (%)": round(ytd_pct, 2),
      })

summary_df = pd.DataFrame(summary_rows)


# Color Formatting Function for Streamlit Tables
def color_positive_green_negative_red(val):
  if isinstance(val, (int, float)):
    if val > 0:
      return "color: #008000; font-weight: bold;"  # Green
    elif val < 0:
      return "color: #FF0000; font-weight: bold;"  # Red
  return ""


if not summary_df.empty:
  # Metric Cards Top Banner
  st.subheader("Performance Summary Breakdown")
  col1, col2, col3, col4 = st.columns(4)

  col1.metric("Total Stocks Tracked", len(summary_df["Ticker"].unique()))
  col2.metric("Avg Daily Change", f"{summary_df['Daily Change (%)'].mean():+.2f}%")
  col3.metric(
      "Avg 30-Day Change", f"{summary_df['30-Day Change (%)'].mean():+.2f}%"
  )
  col4.metric("Avg YTD Change", f"{summary_df['YTD Change (%)'].mean():+.2f}%")

  st.markdown("---")

  # Table Display Options
  view_type = st.radio(
      "View Layout:",
      ["Grouped by Portfolio Title", "Single Combined Table"],
      horizontal=True,
  )

  pct_cols = ["Daily Change (%)", "30-Day Change (%)", "YTD Change (%)"]

  if view_type == "Grouped by Portfolio Title":
    for cat in selected_portfolios:
      cat_df = summary_df[summary_df["Portfolio"] == cat][
          [
              "Ticker",
              "Current Price",
              "Daily Change (%)",
              "30-Day Change (%)",
              "YTD Change (%)",
          ]
      ]
      if not cat_df.empty:
        st.markdown(f"### 📂 {cat}")

        # Apply color styling to percentage change columns
        styled_cat_df = (
            cat_df.style.format({
                "Current Price": "${:.2f}",
                "Daily Change (%)": "{:+.2f}%",
                "30-Day Change (%)": "{:+.2f}%",
                "YTD Change (%)": "{:+.2f}%",
            })
            if hasattr(cat_df.style, "map")
            else cat_df.style.applymap(
                color_positive_green_negative_red, subset=pct_cols
            )
        )
        if hasattr(cat_df.style, "map"):
          styled_cat_df = styled_cat_df.map(
              color_positive_green_negative_red, subset=pct_cols
          )

        st.dataframe(styled_cat_df, use_container_width=True, hide_index=True)
  else:
    styled_summary_df = (
        summary_df.style.format({
            "Current Price": "${:.2f}",
            "Daily Change (%)": "{:+.2f}%",
            "30-Day Change (%)": "{:+.2f}%",
            "YTD Change (%)": "{:+.2f}%",
        })
        if hasattr(summary_df.style, "map")
        else summary_df.style.applymap(
            color_positive_green_negative_red, subset=pct_cols
        )
    )
    if hasattr(summary_df.style, "map"):
      styled_summary_df = styled_summary_df.map(
          color_positive_green_negative_red, subset=pct_cols
      )

    st.dataframe(styled_summary_df, use_container_width=True, hide_index=True)

  st.markdown("---")

  # Top 7 Performing Stocks (YTD) Section
  st.subheader("Top 7 Performing Stocks (YTD)")
  top_7_df = (
      summary_df.drop_duplicates(subset=["Ticker"])
      .nlargest(7, "YTD Change (%)")
      .reset_index(drop=True)
  )

  top_cols = st.columns(7)
  for idx, row in top_7_df.iterrows():
    with top_cols[idx]:
      st.metric(
          label=row["Ticker"],
          value=f"${row['Current Price']:.2f}",
          delta=f"{row['YTD Change (%)']:+.2f}% YTD",
      )

  # Plotly Chart for Top 7 Performers
  fig = go.Figure()
  for t in top_7_df["Ticker"]:
    if t in df_close.columns:
      s = df_close[t].dropna()
      current_yr = pd.Timestamp.now().year
      s_ytd = s[s.index.year == current_yr]
      if not s_ytd.empty:
        pct_series = ((s_ytd / s_ytd.iloc[0]) - 1) * 100
        fig.add_trace(
            go.Scatter(
                x=pct_series.index,
                y=pct_series,
                mode="lines",
                name=t,
            )
        )

  fig.update_layout(
      title="Top 7 YTD Return Trajectory",
      xaxis_title="Date",
      yaxis_title="YTD Return (%)",
      template="plotly_white",
      height=450,
  )
  st.plotly_chart(fig, use_container_width=True)
