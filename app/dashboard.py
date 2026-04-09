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
from scripts.load_data import load_to_postgres, read_from_postgres

st.set_page_config(
    page_title="Painel B3",
    page_icon="📈",
    layout="wide",
)

# ── Estilos ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="metric-container"] { background:#f8f9fa; border-radius:8px; padding:12px; }
.alert-box { padding:10px 16px; border-radius:6px; font-weight:500; margin-bottom:8px; }
.alert-sell { background:#fff0f0; color:#c0392b; border-left:4px solid #c0392b; }
.alert-buy  { background:#f0fff4; color:#196f3d; border-left:4px solid #27ae60; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def fmt_volume(v: float) -> str:
    if v >= 1_000_000_000:
        return f"{v/1_000_000_000:.1f}B"
    if v >= 1_000_000:
        return f"{v/1_000_000:.1f}M"
    if v >= 1_000:
        return f"{v/1_000:.1f}K"
    return str(int(v))


# ── Carregamento de dados ─────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_data(symbols: list) -> pd.DataFrame:
    """
    Tenta ler do banco primeiro.
    Se não tiver dados, busca na API, transforma e salva.
    """
    df = read_from_postgres(symbols)

    if df.empty:
        with st.spinner("Buscando dados na Brapi..."):
            raw = fetch_stock_data(symbols=symbols)
            df = transform_stock_data(raw)
            if not df.empty:
                load_to_postgres(df)

    return df


# ── Gráfico principal ─────────────────────────────────────────────────────────
def create_chart(df: pd.DataFrame) -> go.Figure:
    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        row_heights=[0.55, 0.2, 0.25],
        subplot_titles=("Candlestick + Médias Móveis", "Volume", "RSI (14)"),
        vertical_spacing=0.06,
    )

    # --- Candlestick ---
    fig.add_trace(
        go.Candlestick(
            x=df["datetime"],
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            name="Preço",
            increasing_line_color="#27ae60",
            decreasing_line_color="#c0392b",
        ),
        row=1, col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=df["datetime"], y=df["ma9"],
            name="MA9", line=dict(color="#e67e22", width=1.5),
        ),
        row=1, col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=df["datetime"], y=df["ma21"],
            name="MA21", line=dict(color="#2980b9", width=1.5),
        ),
        row=1, col=1,
    )

    # --- Volume ---
    colors = [
        "#27ae60" if c >= o else "#c0392b"
        for c, o in zip(df["close"], df["open"])
    ]
    fig.add_trace(
        go.Bar(
            x=df["datetime"], y=df["volume"],
            name="Volume", marker_color=colors, showlegend=False,
        ),
        row=2, col=1,
    )

    # --- RSI ---
    fig.add_trace(
        go.Scatter(
            x=df["datetime"], y=df["rsi"],
            name="RSI", line=dict(color="#8e44ad", width=1.5),
        ),
        row=3, col=1,
    )

    # Zonas RSI
    for y_val, color, label in [(70, "rgba(192,57,43,0.12)", "Sobrecomprado"),
                                 (30, "rgba(39,174,96,0.12)", "Sobrevendido")]:
        fig.add_hline(
            y=y_val, line_dash="dash",
            line_color="#c0392b" if y_val == 70 else "#27ae60",
            line_width=1, row=3, col=1,
            annotation_text=label,
            annotation_position="right",
        )

    fig.update_layout(
        height=750,
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", y=1.02, x=0),
        margin=dict(t=40, b=10),
        plot_bgcolor="white",
        paper_bgcolor="white",
    )
    fig.update_yaxes(gridcolor="#f0f0f0")

    return fig


# ── App principal ─────────────────────────────────────────────────────────────
def main():
    st.title("📈 Painel de Ativos — B3")

    # Sidebar: configuração de ativos
    with st.sidebar:
        st.header("⚙️ Configurações")

        simbolos_input = st.text_input(
            "Ativos (separados por vírgula)",
            value="VALE3, PETR4, ITUB4",
            help="Ex: VALE3, MGLU3, BBAS3",
        )
        simbolos = [s.strip().upper() for s in simbolos_input.split(",") if s.strip()]

        atualizar = st.button("🔄 Atualizar dados", use_container_width=True)
        if atualizar:
            st.cache_data.clear()
            st.rerun()

        st.divider()
        st.caption("Dados via Brapi · Armazenados em PostgreSQL")

    # Carrega dados
    df = load_data(simbolos)

    if df.empty:
        st.error("Nenhum dado disponível. Verifique os símbolos ou a conexão com a API.")
        st.stop()

    # Seleção de ativo
    ativos_disponiveis = sorted(df["symbol"].unique().tolist())
    ativo_selecionado = st.selectbox("Selecione o ativo", ativos_disponiveis)

    filtrado = df[df["symbol"] == ativo_selecionado].sort_values("datetime").copy()
    latest = filtrado.iloc[-1]
    anterior = filtrado.iloc[-2] if len(filtrado) > 1 else latest

    # ── Alertas RSI ──────────────────────────────────────────────────────────
    if latest["rsi_signal"] == "Sobrecomprado":
        st.markdown(
            f'<div class="alert-box alert-sell">🔴 RSI em {latest["rsi"]:.1f} — '
            f'<b>{ativo_selecionado}</b> pode estar sobrecomprado. Atenção para possível correção.</div>',
            unsafe_allow_html=True,
        )
    elif latest["rsi_signal"] == "Sobrevendido":
        st.markdown(
            f'<div class="alert-box alert-buy">🟢 RSI em {latest["rsi"]:.1f} — '
            f'<b>{ativo_selecionado}</b> pode estar sobrevendido. Possível oportunidade de entrada.</div>',
            unsafe_allow_html=True,
        )

    # ── Métricas ─────────────────────────────────────────────────────────────
    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "Preço atual",
        f"R$ {latest['close']:.2f}",
        delta=f"{latest['daily_change_pct']:.2f}%",
    )
    col2.metric(
        "Variação diária",
        f"{latest['daily_change_pct']:.2f}%",
        delta=f"{latest['daily_change_pct'] - anterior['daily_change_pct']:.2f}% vs ontem",
    )
    col3.metric("Tendência", latest["trend"])
    col4.metric("RSI", f"{latest['rsi']:.1f}", delta=latest["rsi_signal"])
    col5.metric("Volume", fmt_volume(latest["volume"]))

    # ── Gráfico ──────────────────────────────────────────────────────────────
    st.subheader("📊 Gráfico")
    fig = create_chart(filtrado)
    st.plotly_chart(fig, use_container_width=True)

    # ── Tabela recente ────────────────────────────────────────────────────────
    with st.expander("📋 Dados recentes (últimos 20 pregões)"):
        colunas = ["datetime", "open", "high", "low", "close", "volume",
                   "ma9", "ma21", "rsi", "rsi_signal", "trend", "daily_change_pct"]
        st.dataframe(
            filtrado[colunas].tail(20).sort_values("datetime", ascending=False),
            use_container_width=True,
        )


if __name__ == "__main__":
    main()