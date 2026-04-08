import pandas as pd


def transform_stock_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforma os dados brutos de ações:
    - ordena por símbolo e data
    - calcula médias móveis de 9 e 21 períodos
    - cria coluna de tendência
    """

    if df.empty:
        print("DataFrame vazio. Nada para transformar.")
        return df

    # garante cópia para evitar problemas
    df = df.copy()

    # padroniza tipos
    df["datetime"] = pd.to_datetime(df["datetime"])
    df["symbol"] = df["symbol"].astype(str)

    numeric_columns = ["open", "high", "low", "close", "volume"]
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # ordena corretamente
    df = df.sort_values(["symbol", "datetime"]).reset_index(drop=True)

    # médias móveis por ativo
    df["ma9"] = df.groupby("symbol")["close"].transform(
        lambda x: x.rolling(window=9).mean()
    )

    df["ma21"] = df.groupby("symbol")["close"].transform(
        lambda x: x.rolling(window=21).mean()
    )

    # tendência simples
    df["trend"] = df.apply(
        lambda row: "Alta" if pd.notnull(row["ma21"]) and row["close"] > row["ma21"] else "Baixa",
        axis=1
    )

    return df


if __name__ == "__main__":
    from fetch_data import fetch_stock_data

    raw_df = fetch_stock_data()
    transformed_df = transform_stock_data(raw_df)

    print(transformed_df.head(15))
    print(transformed_df.tail(15))
    print(transformed_df.columns)