import time
import pandas as pd
import requests

DEFAULT_SYMBOLS = ["VALE3", "PETR4", "ITUB4"]

# Endpoint que aceita múltiplos símbolos de uma vez (ex: VALE3,PETR4,ITUB4)
BASE_URL = "https://brapi.dev/api/quote/{symbols}?range=3mo&interval=1d&fundamental=false"

MAX_RETRIES = 3
RETRY_DELAY = 2


def _parse_results(results: list) -> pd.DataFrame:
    """Extrai e normaliza os dados históricos de uma resposta da Brapi."""
    all_data = []

    for result in results:
        symbol = result.get("symbol", "")
        historical = result.get("historicalDataPrice", [])

        if not historical:
            print(f"[{symbol}] Sem dados históricos.")
            continue

        df = pd.DataFrame(historical)
        df["datetime"] = pd.to_datetime(df["date"], unit="s")
        df["symbol"] = symbol
        df = df[["symbol", "datetime", "open", "high", "low", "close", "volume"]]
        df = df.sort_values("datetime").reset_index(drop=True)

        print(f"[{symbol}] {len(df)} registros carregados.")
        all_data.append(df)

    if not all_data:
        return pd.DataFrame()

    return pd.concat(all_data, ignore_index=True)


def fetch_stock_data(symbols: list = None) -> pd.DataFrame:
    """
    Busca dados históricos de múltiplos ativos em uma única chamada à Brapi.

    A Brapi aceita vários símbolos separados por vírgula no mesmo endpoint,
    o que é mais rápido e evita problemas de cache do Streamlit com listas.
    """
    if symbols is None:
        symbols = DEFAULT_SYMBOLS

    # Normaliza e remove duplicatas mantendo a ordem
    symbols_clean = list(dict.fromkeys(s.upper().strip() for s in symbols if s.strip()))

    if not symbols_clean:
        print("Nenhum símbolo válido fornecido.")
        return pd.DataFrame()

    # Junta todos os símbolos em uma única URL
    symbols_str = ",".join(symbols_clean)
    url = BASE_URL.format(symbols=symbols_str)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"Buscando: {symbols_str} (tentativa {attempt}/{MAX_RETRIES})")
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            data = response.json()
            results = data.get("results", [])

            if not results:
                print("Nenhum resultado retornado pela API.")
                return pd.DataFrame()

            final_df = _parse_results(results)
            print(f"\nTotal: {len(final_df)} registros de {final_df['symbol'].nunique()} ativo(s).")
            return final_df

        except requests.exceptions.Timeout:
            print(f"Timeout na tentativa {attempt}/{MAX_RETRIES}.")
        except requests.exceptions.HTTPError as e:
            print(f"Erro HTTP: {e}")
            break
        except Exception as e:
            print(f"Erro inesperado: {e}")

        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY)

    return pd.DataFrame()


if __name__ == "__main__":
    df = fetch_stock_data()
    print(df.head())