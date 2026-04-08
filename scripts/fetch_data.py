import requests
import pandas as pd

SYMBOLS = ["PETR4", "VALE3", "ITUB4"]

def fetch_stock_data():
    all_data = []

    for symbol in SYMBOLS:
        print(f"Buscando dados de {symbol}...")

        url = f"https://brapi.dev/api/quote/{symbol}?range=3mo&interval=1d"

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            data = response.json()

            results = data.get("results", [])
            if not results:
                print(f"Nenhum dado encontrado para {symbol}")
                continue

            historical = results[0].get("historicalDataPrice", [])
            if not historical:
                print(f"Sem histórico para {symbol}")
                continue

            df = pd.DataFrame(historical)

            # converte timestamp unix para data
            df["datetime"] = pd.to_datetime(df["date"], unit="s")

            # adiciona símbolo
            df["symbol"] = symbol

            # seleciona colunas principais
            df = df[["symbol", "datetime", "open", "high", "low", "close", "volume"]]

            all_data.append(df)

        except Exception as e:
            print(f"Erro ao buscar {symbol}: {e}")

    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        return final_df

    return pd.DataFrame()

if __name__ == "__main__":
    df = fetch_stock_data()
    print(df.head())
    print(df.tail())
    print(df["symbol"].value_counts() if not df.empty else "DataFrame vazio")