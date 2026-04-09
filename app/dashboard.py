import streamlit as st
import pandas as pd
import os
import sys

# garante que a raiz do projeto entre no path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.fetch_data import fetch_stock_data
from scripts.transform_data import transform_stock_data

st.set_page_config(page_title="Brazil Stock Dashboard", layout="wide")


@st.cache_data(ttl=3600)
def load_data():
    raw_df = fetch_stock_data()
    df = transform_stock_data(raw_df)
    return df


st.title("📈 Brazil Stock Dashboard")

df = load_data()

if df.empty:
    st.warning("No data found.")
    st.stop()

symbols = sorted(df["symbol"].unique())
selected_symbol = st.selectbox("Select a stock", symbols)

filtered_df = df[df["symbol"] == selected_symbol].copy()
filtered_df = filtered_df.sort_values("datetime")

latest = filtered_df.iloc[-1]

col1, col2, col3 = st.columns(3)
col1.metric("Current Price", f"R$ {latest['close']:.2f}")
col2.metric("Trend", latest["trend"])
col3.metric("Volume", f"{int(latest['volume'])}")

st.subheader("Price and Moving Averages")
chart_df = filtered_df.set_index("datetime")[["close", "ma9", "ma21"]]
st.line_chart(chart_df)

st.subheader("Recent Data")
st.dataframe(filtered_df.sort_values("datetime", ascending=False).head(20))