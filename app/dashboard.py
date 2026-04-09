import os
import sys

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

# Garante que a raiz do projeto esteja no path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

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
        vertical_spacing=0.03,
        row_heights=[0.7, 0.3],
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
        height=650,
        margin=dict(l=10, r=10, t=50, b=10),
    )

    fig.update_yaxes(title_text="Price (R$)", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)

    return fig


def main() -> None:
    st.title("📈 Brazil Stock Dashboard")

    df = load_data()

    if df.empty:
        st.warning("No data found.")
        st.stop()

    df["datetime"] = pd.to_datetime(df["datetime"])

    symbols = sorted(df["symbol"].unique())
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

    st.subheader("📊 Professional Chart")
    fig = create_candlestick_chart(filtered_df)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📋 Recent Data")
    st.dataframe(
        filtered_df.sort_values("datetime", ascending=False).reset_index(drop=True),
        use_container_width=True,
    )


if __name__ == "__main__":
    main()