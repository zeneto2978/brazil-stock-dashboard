import os
import sys

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from scripts.fetch_data import fetch_stock_data
from scripts.transform_data import transform_stock_data


st.set_page_config(page_title="Brazil Stock Dashboard", layout="wide")


@st.cache_data(ttl=3600)
def load_data() -> pd.DataFrame:
    raw_df = fetch_stock_data()
    transformed_df = transform_stock_data(raw_df)
    return transformed_df


def create_candlestick_chart(filtered_df: pd.DataFrame) -> go.Figure:
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.04,
        row_heights=[0.72, 0.28],
    )

    fig.add_trace(
        go.Candlestick(
            x=filtered_df["datetime"],
            open=filtered_df["open"],
            high=filtered_df["high"],
            low=filtered_df["low"],
            close=filtered_df["close"],
            name="Price",
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=filtered_df["datetime"],
            y=filtered_df["ma9"],
            mode="lines",
            name="MA9",
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=filtered_df["datetime"],
            y=filtered_df["ma21"],
            mode="lines",
            name="MA21",
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Bar(
            x=filtered_df["datetime"],
            y=filtered_df["volume"],
            name="Volume",
        ),
        row=2,
        col=1,
    )

    fig.update_layout(
        title="Price, Moving Averages and Volume",
        xaxis_rangeslider_visible=False,
        height=700,
        margin=dict(l=10, r=10, t=50, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )

    fig.update_yaxes(title_text="Price (R$)", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)

    return fig


def main() -> None:
    st.title("📈 Brazil Stock Dashboard")
    st.caption("Brazilian stocks dashboard with price, moving averages and volume.")

    df = load_data()

    if df.empty:
        st.error("No market data could be loaded.")
        st.stop()

    df["datetime"] = pd.to_datetime(df["datetime"])
    symbols = sorted(df["symbol"].dropna().unique().tolist())

    st.sidebar.header("Dashboard Settings")
    st.sidebar.write("Loaded symbols:")
    for symbol in symbols:
        count_rows = int((df["symbol"] == symbol).sum())
        st.sidebar.write(f"- {symbol}: {count_rows} rows")

    if len(symbols) < 3:
        st.sidebar.warning(
            "Some symbols were not loaded from the API. This can happen temporarily."
        )

    if not symbols:
        st.error("No symbols available.")
        st.stop()

    selected_symbol = st.selectbox("Select a stock", symbols)

    filtered_df = df[df["symbol"] == selected_symbol].copy()
    filtered_df = filtered_df.sort_values("datetime")

    if filtered_df.empty:
        st.warning("No data available for the selected stock.")
        st.stop()

    latest = filtered_df.iloc[-1]

    col1, col2, col3 = st.columns(3)
    col1.metric("Current Price", f"R$ {latest['close']:.2f}")
    col2.metric("Trend", latest["trend"])
    col3.metric("Volume", f"{int(latest['volume'])}")

    st.subheader(f"📊 {selected_symbol} Chart")
    fig = create_candlestick_chart(filtered_df)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📋 Recent Data")
    recent_df = (
        filtered_df.sort_values("datetime", ascending=False)
        .reset_index(drop=True)
        .head(20)
    )
    st.dataframe(recent_df, use_container_width=True)


if __name__ == "__main__":
    main()