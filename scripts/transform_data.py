import numpy as np
import pandas as pd


def _compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """
    Calcula o RSI (Relative Strength Index) de uma série de preços.
    Retorna valores entre 0 e 100.
    """
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi


def transform_stock_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica transformações e calcula indicadores técnicos:
    - Médias móveis (MA9, MA21)
    - Variação diária percentual
    - Tendência (vetorizada)
    - RSI (14 períodos)
    - Sinal de alerta baseado no RSI
    """
    if df.empty:
        return df

    df = df.copy()
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.sort_values(["symbol", "datetime"]).reset_index(drop=True)

    grp = df.groupby("symbol")["close"]

    # Médias móveis
    df["ma9"] = grp.transform(lambda x: x.rolling(9, min_periods=1).mean())
    df["ma21"] = grp.transform(lambda x: x.rolling(21, min_periods=1).mean())

    # Variação diária
    df["daily_change_pct"] = grp.pct_change() * 100

    # Tendência — vetorizada (muito mais rápido que apply linha a linha)
    df["trend"] = np.where(df["close"] > df["ma21"], "Uptrend", "Downtrend")

    # RSI por símbolo
    df["rsi"] = grp.transform(_compute_rsi)

    # Sinal de alerta baseado no RSI
    # RSI < 30 → sobrevendido (possível compra)
    # RSI > 70 → sobrecomprado (possível venda)
    df["rsi_signal"] = np.select(
        [df["rsi"] < 30, df["rsi"] > 70],
        ["Sobrevendido", "Sobrecomprado"],
        default="Neutro"
    )

    return df


if __name__ == "__main__":
    from fetch_data import fetch_stock_data

    raw = fetch_stock_data()
    transformed = transform_stock_data(raw)
    print(transformed[["symbol", "datetime", "close", "ma9", "ma21", "rsi", "rsi_signal", "trend"]].tail(10))