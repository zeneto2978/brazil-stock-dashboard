import time
from typing import List, Tuple

import pandas as pd
import requests

SYMBOLS = [
    "VALE3",
    "PETR4",
    "WEGE3",
]

BASE_URL = "https://brapi.dev/api/quote/{symbol}?range=3mo&interval=1d"


def fetch_one_symbol(symbol: str, max_retries: int = 3, sleep_seconds: int = 2) -> pd.DataFrame:
    for attempt in range(1, max_retries + 1):
        try:
            url = BASE_URL.format(symbol=symbol)
            response = requests.get(url, timeout=20)
            response.raise_for_status()

            payload = response.json()
            results = payload.get("results", [])

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
            print(f"[ERROR] {symbol}: attempt {attempt}/{max_retries} failed -> {exc}")
            if attempt < max_retries:
                time.sleep(sleep_seconds)

    return pd.DataFrame()


def fetch_stock_data(symbols: List[str] | None = None) -> Tuple[pd.DataFrame, List[str], List[str]]:
    if symbols is None:
        symbols = SYMBOLS

    all_data = []
    loaded_symbols = []
    failed_symbols = []

    for symbol in symbols:
        df = fetch_one_symbol(symbol)

        if df.empty:
            failed_symbols.append(symbol)
        else:
            all_data.append(df)
            loaded_symbols.append(symbol)

        time.sleep(1)

    if not all_data:
        return pd.DataFrame(), loaded_symbols, failed_symbols

    final_df = pd.concat(all_data, ignore_index=True)
    final_df = final_df.sort_values(["symbol", "datetime"]).reset_index(drop=True)

    print("\n=== LOAD SUMMARY ===")
    print("Loaded symbols:", loaded_symbols)
    print("Failed symbols:", failed_symbols)
    print("\nRows by symbol:")
    print(final_df["symbol"].value_counts())

    return final_df, loaded_symbols, failed_symbols


if __name__ == "__main__":
    df, loaded, failed = fetch_stock_data()
    print(df.head())
    print("\nLoaded:", loaded)
    print("Failed:", failed)