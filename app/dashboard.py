import os
import sys
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# garante import correto no Streamlit Cloud
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from scripts.fetch_data import fetch_stock_data
from scripts.transform_data import transform_stock_data


st.set_page_config(page_title="Brazil Stock Dashboard", layout="wide")


@st.cache_data(ttl=3600)
def load_data():
    raw_df = fetch_stock_data()
    df = transform_stock_data(raw_df)
    return df


def create_chart(df):
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.7, 0.3],
    )

    fig.add_trace(
        go.Candlestick(
            x=df["datetime"],
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            name="Price",
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(x=df["datetime"], y=df["ma9"], name="MA9"),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(x=df["datetime"], y=df["ma21"], name="MA21"),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Bar(x=df["datetime"], y=df["volume"], name="Volume"),
        row=2,
        col=1,
    )

    fig.update_layout(
        height=650,
        xaxis_rangeslider_visible=False,
        margin=dict(l=10, r=10, t=30, b=10),
    )

    return fig


def main():
    st.title("📈 Brazil Stock Dashboard")

    df = load_data()

    if df.empty:
        st.error("No data loaded")
        st.stop()

    st.write("### DEBUG — Symbols loaded:")
    st.write(df["symbol"].value_counts())

    symbols = sorted(df["symbol"].unique())

    if not symbols:
        st.error("No symbols available")
        st.stop()

    selected_symbol = st.selectbox("Select a stock", symbols)

    filtered_df = df[df["symbol"] == selected_symbol].copy()
    filtered_df = filtered_df.sort_values("datetime")

    latest = filtered_df.iloc[-1]

    col1, col2, col3 = st.columns(3)

    col1.metric("Price", f"R$ {latest['close']:.2f}")
    col2.metric("Trend", latest["trend"])
    col3.metric("Volume", int(latest["volume"]))

    st.subheader("📊 Professional Chart")

    fig = create_chart(filtered_df)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📋 Recent Data")
    st.dataframe(filtered_df.tail(20))


if __name__ == "__main__":
    main()