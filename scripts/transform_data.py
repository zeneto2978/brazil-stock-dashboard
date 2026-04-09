import pandas as pd


def transform_stock_data(df: pd.DataFrame):
    if df.empty:
        return df

    df = df.copy()

    df["datetime"] = pd.to_datetime(df["datetime"])

    df = df.sort_values(["symbol", "datetime"])

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