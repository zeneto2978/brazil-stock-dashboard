import requests
import pandas as pd
import time

SYMBOLS = ["PETR4", "VALE3", "ITUB4"]


def fetch_stock_data():
    all_data = []

    for symbol in SYMBOLS:
        print(f"\n📥 Fetching data for {symbol}...")

        url = f"https://brapi.dev/api/quote/{symbol}?range=3mo&interval=1d"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()

            results = data.get("results", [])

            if not results:
                print(f"⚠️ No results for {symbol}")
                continue

            historical = results[0].get("historicalDataPrice", [])

            if not historical:
                print(f"⚠️ No historical data for {symbol}")
                continue

            df = pd.DataFrame(historical)

            df["datetime"] = pd.to_datetime(df["date"], unit="s")
            df["symbol"] = symbol

            df = df[["symbol", "datetime", "open", "high", "low", "close", "volume"]]

            print(f"✅ {symbol} loaded with {len(df)} rows")

            all_data.append(df)

            time.sleep(1)

        except Exception as e:
            print(f"❌ Error fetching {symbol}: {e}")

    if not all_data:
        print("🚨 No data collected at all!")
        return pd.DataFrame()

    final_df = pd.concat(all_data, ignore_index=True)

    print("\n📊 Summary:")
    print(final_df["symbol"].value_counts())

    return final_df


if __name__ == "__main__":
    df = fetch_stock_data()
    print(df.head())