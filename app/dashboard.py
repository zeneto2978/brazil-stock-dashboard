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


st.set_page_config(
    page_title="Brazil Stock Dashboard",
    layout="wide",
)


@st.cache_data(ttl=3600)
def load_data():
    raw_df, loaded_symbols, failed_symbols = fetch_stock_data()
    transformed_df = transform_stock_data(raw_df)
    return transformed_df, loaded_symbols, failed_symbols


def create_candlestick_chart(filtered_df: pd.DataFrame, symbol: str) -> go.Figure:
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.06,
        row_heights=[0.72, 0.28],
        subplot_titles=(f"{symbol} Price", "Volume"),
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
        height=760,
        xaxis_rangeslider_visible=False,
        margin=dict(l=20, r=20, t=70, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ),
    )

    fig.update_yaxes(title_text="Price (R$)", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)

    return fig


def format_volume(value: float) -> str:
    return f"{int(value):,}".replace(",", ".")


def main():
    st.title("📈 Brazil Stock Dashboard")
    st.caption("Brazilian stocks dashboard with price, moving averages and volume.")

    df, loaded_symbols, failed_symbols = load_data()

    if df.empty:
        st.error("No market data could be loaded.")
        st.stop()

    df["datetime"] = pd.to_datetime(df["datetime"])
    available_symbols = sorted(df["symbol"].dropna().unique().tolist())

    if not available_symbols:
        st.error("No symbols available.")
        st.stop()

    if failed_symbols:
        st.warning(
            "Some symbols could not be loaded from the API at this moment: "
            + ", ".join(failed_symbols)
        )

    top_col1, top_col2 = st.columns([2, 1])

    with top_col1:
        selected_symbol = st.selectbox("Select a stock", available_symbols, index=0)

    with top_col2:
        st.write("")
        st.write("")
        st.info(f"Loaded assets: {len(available_symbols)}")

    filtered_df = df[df["symbol"] == selected_symbol].copy()
    filtered_df = filtered_df.sort_values("datetime").reset_index(drop=True)

    if filtered_df.empty:
        st.warning("No data available for the selected stock.")
        st.stop()

    latest = filtered_df.iloc[-1]
    previous = filtered_df.iloc[-2] if len(filtered_df) > 1 else latest

    price_delta = latest["close"] - previous["close"]
    pct_delta = latest["daily_change_pct"] if pd.notnull(latest["daily_change_pct"]) else 0.0

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Current Price",
        f"R$ {latest['close']:.2f}",
        f"{price_delta:.2f}",
    )
    col2.metric(
        "Daily Change %",
        f"{pct_delta:.2f}%",
    )
    col3.metric(
        "Trend",
        latest["trend"],
    )
    col4.metric(
        "Volume",
        format_volume(latest["volume"]),
    )

    st.markdown("---")

    chart_col, summary_col = st.columns([3.2, 1.2], gap="large")

    with chart_col:
        st.subheader(f"📊 {selected_symbol} Chart")
        fig = create_candlestick_chart(filtered_df, selected_symbol)
        st.plotly_chart(fig, use_container_width=True)

    with summary_col:
        st.subheader("Summary")
        st.write(f"**Symbol:** {selected_symbol}")
        st.write(f"**Last date:** {latest['datetime'].date()}")
        st.write(f"**Open:** R$ {latest['open']:.2f}")
        st.write(f"**High:** R$ {latest['high']:.2f}")
        st.write(f"**Low:** R$ {latest['low']:.2f}")
        st.write(f"**Close:** R$ {latest['close']:.2f}")

        ma9_value = "N/A" if pd.isnull(latest["ma9"]) else f"R$ {latest['ma9']:.2f}"
        ma21_value = "N/A" if pd.isnull(latest["ma21"]) else f"R$ {latest['ma21']:.2f}"

        st.write(f"**MA9:** {ma9_value}")
        st.write(f"**MA21:** {ma21_value}")

    st.markdown("---")

    st.subheader("📋 Recent Data")
    recent_df = (
        filtered_df.sort_values("datetime", ascending=False)
        .reset_index(drop=True)
        .head(20)
    )

    recent_df = recent_df[
        ["datetime", "open", "high", "low", "close", "volume", "ma9", "ma21", "trend"]
    ]

    st.dataframe(recent_df, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()