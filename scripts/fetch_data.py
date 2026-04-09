import time
import pandas as pd
import requests

SYMBOLS = ["VALE3", "PETR4", "WEGE3"]

BASE_URL = "https://brapi.dev/api/quote/{symbol}?range=3mo&interval=1d"


def fetch_one_symbol(symbol: str):
    try:
        url = BASE_URL.format(symbol=symbol)
        response = requests.get(url, timeout=20)
        response.raise_for_status()

        data = response.json()
        results = data.get("results", [])

        if not results:
            return pd.DataFrame()

        historical = results[0].get("historicalDataPrice", [])

        if not historical:
            return pd.DataFrame()

        df = pd.DataFrame(historical)

        df["datetime"] = pd.to_datetime(df["date"], unit="s")
        df["symbol"] = symbol

        df = df[["symbol", "datetime", "open", "high", "low", "close", "volume"]]
        df = df.sort_values("datetime")

        return df

    except Exception as e:
        print(f"Error loading {symbol}: {e}")
        return pd.DataFrame()


def fetch_stock_data():
    all_data = []

    for symbol in SYMBOLS:
        df = fetch_one_symbol(symbol)

        if not df.empty:
            all_data.append(df)

        time.sleep(1)

    if not all_data:
        return pd.DataFrame()

    final_df = pd.concat(all_data, ignore_index=True)
    return final_df


if __name__ == "__main__":
    df = fetch_stock_data()
    print(df.head())