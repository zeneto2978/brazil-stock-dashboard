import pandas as pd


def transform_stock_data(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    df = df.copy()
    df["datetime"] = pd.to_datetime(df["datetime"])
    df["symbol"] = df["symbol"].astype(str)

    numeric_columns = ["open", "high", "low", "close", "volume"]
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.sort_values(["symbol", "datetime"]).reset_index(drop=True)

    df["ma9"] = df.groupby("symbol")["close"].transform(
        lambda x: x.rolling(9).mean()
    )

    df["ma21"] = df.groupby("symbol")["close"].transform(
        lambda x: x.rolling(21).mean()
    )

    df["daily_change_pct"] = df.groupby("symbol")["close"].pct_change() * 100

    df["trend"] = df.apply(
        lambda row: "Uptrend"
        if pd.notnull(row["ma21"]) and row["close"] > row["ma21"]
        else "Downtrend",
        axis=1,
    )

    return df


if __name__ == "__main__":
    from scripts.fetch_data import fetch_stock_data

    raw_df = fetch_stock_data()
    transformed_df = transform_stock_data(raw_df)

    print(transformed_df.head(15))
    print(transformed_df.tail(15))