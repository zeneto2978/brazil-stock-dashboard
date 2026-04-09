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
    raw_result = fetch_stock_data()

    # Compatibilidade:
    # - se fetch_stock_data() retornar só DataFrame
    # - ou se retornar (DataFrame, loaded_symbols, failed_symbols)
    if isinstance(raw_result, tuple):
        raw_df = raw_result[0]
    else:
        raw_df = raw_result

    df = transform_stock_data(raw_df)
    return df


def create_chart(df: pd.DataFrame) -> go.Figure:
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        row_heights=[0.7, 0.3],
        vertical_spacing=0.05,
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
        go.Scatter(
            x=df["datetime"],
            y=df["ma9"],
            mode="lines",
            name="MA9",
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=df["datetime"],
            y=df["ma21"],
            mode="lines",
            name="MA21",
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Bar(
            x=df["datetime"],
            y=df["volume"],
            name="Volume",
        ),
        row=2,
        col=1,
    )

    fig.update_layout(
        height=700,
        xaxis_rangeslider_visible=False,
        margin=dict(l=20, r=20, t=40, b=20),
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


def main() -> None:
    st.title("📈 Brazil Stock Dashboard")
    st.caption("Brazilian stocks dashboard with price, moving averages and volume.")

    df = load_data()

    if df.empty:
        st.error("No data loaded.")
        st.stop()

    df["datetime"] = pd.to_datetime(df["datetime"])
    symbols = sorted(df["symbol"].dropna().unique().tolist())

    if not symbols:
        st.error("No symbols available.")
        st.stop()

    selected_symbol = st.selectbox("Select a stock", symbols)

    filtered_df = df[df["symbol"] == selected_symbol].copy()
    filtered_df = filtered_df.sort_values("datetime").reset_index(drop=True)

    if filtered_df.empty:
        st.warning(f"No data available for {selected_symbol}.")
        st.stop()

    latest = filtered_df.iloc[-1]

    if len(filtered_df) > 1:
        previous = filtered_df.iloc[-2]
        price_delta = latest["close"] - previous["close"]
    else:
        price_delta = 0.0

    if "daily_change_pct" in filtered_df.columns and pd.notnull(latest["daily_change_pct"]):
        pct_delta = latest["daily_change_pct"]
    else:
        pct_delta = 0.0

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Price", f"R$ {latest['close']:.2f}", f"{price_delta:.2f}")
    col2.metric("Change %", f"{pct_delta:.2f}%")
    col3.metric("Trend", str(latest["trend"]))
    col4.metric("Volume", f"{int(latest['volume']):,}".replace(",", "."))

    st.subheader("📊 Chart")
    fig = create_chart(filtered_df)
    st.plotly_chart(fig, width="stretch")

    st.subheader("📋 Recent Data")
    recent_df = filtered_df.tail(20).sort_values("datetime", ascending=False).reset_index(drop=True)
    st.dataframe(recent_df, width="stretch", hide_index=True)


if __name__ == "__main__":
    main()