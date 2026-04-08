import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from config.settings import DB_CONFIG

st.set_page_config(page_title="Brazil Stock Dashboard", layout="wide")


def get_engine():
    connection_string = (
        f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
        f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    )
    return create_engine(connection_string)


@st.cache_data
def load_data():
    engine = get_engine()
    query = "SELECT * FROM stock_prices"
    df = pd.read_sql(query, engine)
    return df


st.title("📈 Brazil Stock Dashboard")

df = load_data()

if df.empty:
    st.warning("Nenhum dado encontrado.")
    st.stop()

# seleção de ativo
symbols = sorted(df["symbol"].unique())
selected_symbol = st.selectbox("👉🏼 Selecione o ativo", symbols)

# filtrar dados
filtered_df = df[df["symbol"] == selected_symbol].copy()

# pegar último registro
latest = filtered_df.sort_values("datetime").iloc[-1]

# métricas
col1, col2, col3 = st.columns(3)

col1.metric("Preço atual", f"R$ {latest['close']:.2f}")
col2.metric("Tendência", latest["trend"])
col3.metric("Volume", f"{int(latest['volume'])}")

# gráfico
st.subheader("📊 Preço e Médias Móveis")

st.line_chart(
    filtered_df.set_index("datetime")[["close", "ma9", "ma21"]]
)

# tabela
st.subheader("📋 Dados recentes")
st.dataframe(filtered_df.sort_values("datetime", ascending=False).head(20))