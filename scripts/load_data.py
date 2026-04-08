import pandas as pd
from sqlalchemy import create_engine
from config.settings import DB_CONFIG


def get_engine():
    connection_string = (
        f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
        f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    )
    return create_engine(connection_string)


def load_to_postgres(df: pd.DataFrame):
    if df.empty:
        print("DataFrame vazio. Nada para salvar.")
        return

    engine = get_engine()

    df.to_sql(
        "stock_prices",
        engine,
        if_exists="replace",  # substitui tabela
        index=False
    )

    print("Dados salvos no PostgreSQL com sucesso!")


if __name__ == "__main__":
    from fetch_data import fetch_stock_data
    from transform_data import transform_stock_data

    raw_df = fetch_stock_data()
    transformed_df = transform_stock_data(raw_df)

    load_to_postgres(transformed_df)