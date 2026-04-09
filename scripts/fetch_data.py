import time
import requests
import pandas as pd

SYMBOLS = ["PETR4", "VALE3", "ITUB4"]


def fetch_one_symbol(symbol: str) -> pd.DataFrame:
    url = f"https://brapi.dev/api/quote/{symbol}?range=3mo&interval=1d"

    response = requests.get(url, timeout=15)
    response.raise_for_status()

    data = response.json()
    results = data.get("results", [])

    if not results:
        return pd.DataFrame()

    historical = results[0].get("historicalDataPrice", [])
    if not historical:
        return pd.DataFrame()

    df = pd.DataFrame(historical)

    required_columns = {"date", "open", "high", "low", "close", "volume"}
    if not required_columns.issubset(df.columns):
        return pd.DataFrame()

    df["datetime"] = pd.to_datetime(df["date"], unit="s")
    df["symbol"] = symbol

    df = df[["symbol", "datetime", "open", "high", "low", "close", "volume"]]
    return df


def fetch_stock_data() -> pd.DataFrame:
    all_data = []
    loaded_symbols = []
    failed_symbols = []

    for symbol in SYMBOLS:
        try:
            df = fetch_one_symbol(symbol)

            if df.empty:
                failed_symbols.append(symbol)
            else:
                all_data.append(df)
                loaded_symbols.append(symbol)

            time.sleep(1)

        except Exception:
            failed_symbols.append(symbol)

    if not all_data:
        return pd.DataFrame()

    final_df = pd.concat(all_data, ignore_index=True)

    print("\nLoaded symbols:", loaded_symbols)
    print("Failed symbols:", failed_symbols)
    print("\nRows by symbol:")
    print(final_df["symbol"].value_counts())

    return final_df


if __name__ == "__main__":
    df = fetch_stock_data()
    print(df.head())
    print(df["symbol"].value_counts() if not df.empty else "No data loaded.")