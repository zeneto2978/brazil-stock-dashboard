import time
import pandas as pd
import requests

SYMBOLS = ["VALE3", "PETR4", "ITUB4"]

BASE_URL = "https://brapi.dev/api/quote/{symbol}?range=3mo&interval=1d"


def fetch_one_symbol(symbol: str) -> pd.DataFrame:
    try:
        url = BASE_URL.format(symbol=symbol)
        response = requests.get(url, timeout=20)
        response.raise_for_status()

        data = response.json()
        results = data.get("results", [])

        if not results:
            print(f"[WARN] {symbol}: no results returned")
            return pd.DataFrame()

        historical = results[0].get("historicalDataPrice", [])
        if not historical:
            print(f"[WARN] {symbol}: no historical data returned")
            return pd.DataFrame()

        df = pd.DataFrame(historical)

        required_columns = {"date", "open", "high", "low", "close", "volume"}
        if not required_columns.issubset(df.columns):
            print(f"[WARN] {symbol}: missing required columns")
            return pd.DataFrame()

        df["datetime"] = pd.to_datetime(df["date"], unit="s")
        df["symbol"] = symbol

        df = df[["symbol", "datetime", "open", "high", "low", "close", "volume"]].copy()
        df = df.sort_values("datetime").reset_index(drop=True)

        print(f"[OK] {symbol}: {len(df)} rows loaded")
        return df

    except Exception as exc:
        print(f"[ERROR] {symbol}: {exc}")
        return pd.DataFrame()


def fetch_stock_data() -> pd.DataFrame:
    all_data = []

    for symbol in SYMBOLS:
        df = fetch_one_symbol(symbol)

        if not df.empty:
            all_data.append(df)

        time.sleep(1)

    if not all_data:
        return pd.DataFrame()

    final_df = pd.concat(all_data, ignore_index=True)
    final_df = final_df.sort_values(["symbol", "datetime"]).reset_index(drop=True)
    return final_df


if __name__ == "__main__":
    df = fetch_stock_data()
    print(df.head())
    if not df.empty:
        print(df["symbol"].value_counts())