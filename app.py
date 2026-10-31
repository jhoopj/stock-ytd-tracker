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
    "Pharma": ["NBIX", "AXSM", "PHAT", "IHE", "PPH"],
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
        "AIQ",
        "SMHX",
        "XSD",
        "DTCR",
        "IBOT",
    ],
    "BEST of US":
