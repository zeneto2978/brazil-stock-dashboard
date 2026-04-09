import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from config.settings import DB_CONFIG

TABLE_NAME = "stock_prices"

# Chave de unicidade: um registro é único por símbolo + data
UNIQUE_KEYS = ["symbol", "datetime"]


def get_engine():
    """Cria e retorna a engine de conexão com o PostgreSQL."""
    connection_string = (
        f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
        f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    )
    try:
        engine = create_engine(connection_string)
        # Testa a conexão imediatamente
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Conexão com PostgreSQL estabelecida com sucesso.")
        return engine
    except SQLAlchemyError as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        raise


def _create_table_if_not_exists(engine):
    """
    Cria a tabela stock_prices se ela ainda não existir.
    Isso evita o if_exists='replace' que apagava tudo a cada execução.
    """
    create_sql = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        symbol        VARCHAR(10)  NOT NULL,
        datetime      TIMESTAMP    NOT NULL,
        open          NUMERIC(12, 4),
        high          NUMERIC(12, 4),
        low           NUMERIC(12, 4),
        close         NUMERIC(12, 4),
        volume        BIGINT,
        ma9           NUMERIC(12, 4),
        ma21          NUMERIC(12, 4),
        daily_change_pct NUMERIC(10, 4),
        trend         VARCHAR(20),
        rsi           NUMERIC(8, 4),
        rsi_signal    VARCHAR(20),
        PRIMARY KEY (symbol, datetime)
    );
    """
    with engine.connect() as conn:
        conn.execute(text(create_sql))
        conn.commit()
    print(f"Tabela '{TABLE_NAME}' verificada/criada.")


def load_to_postgres(df: pd.DataFrame):
    """
    Salva os dados no PostgreSQL com lógica de upsert:
    - Insere novos registros
    - Atualiza registros existentes (mesmo símbolo + data)
    - Nunca apaga dados históricos
    """
    if df.empty:
        print("DataFrame vazio. Nada para salvar.")
        return

    try:
        engine = get_engine()
        _create_table_if_not_exists(engine)

        # Estratégia: insert em tabela temporária + upsert na principal
        temp_table = f"{TABLE_NAME}_temp"

        with engine.connect() as conn:
            # Salva em tabela temporária (substituição total é segura aqui)
            df.to_sql(temp_table, conn, if_exists="replace", index=False)

            # Colunas para atualizar no conflito
            update_cols = [
                c for c in df.columns if c not in UNIQUE_KEYS
            ]
            update_set = ", ".join(
                [f"{col} = EXCLUDED.{col}" for col in update_cols]
            )

            upsert_sql = f"""
            INSERT INTO {TABLE_NAME}
            SELECT * FROM {temp_table}
            ON CONFLICT (symbol, datetime)
            DO UPDATE SET {update_set};
            """
            conn.execute(text(upsert_sql))
            conn.execute(text(f"DROP TABLE IF EXISTS {temp_table}"))
            conn.commit()

        print(f"{len(df)} registros salvos/atualizados em '{TABLE_NAME}' com sucesso!")

    except SQLAlchemyError as e:
        print(f"Erro ao salvar no banco de dados: {e}")
        raise


def read_from_postgres(symbols: list = None) -> pd.DataFrame:
    """
    Lê dados do banco para uso no Streamlit.
    Filtra por símbolo se fornecido.
    """
    try:
        engine = get_engine()

        if symbols:
            placeholders = ", ".join([f"'{s}'" for s in symbols])
            query = f"SELECT * FROM {TABLE_NAME} WHERE symbol IN ({placeholders}) ORDER BY symbol, datetime"
        else:
            query = f"SELECT * FROM {TABLE_NAME} ORDER BY symbol, datetime"

        df = pd.read_sql(query, engine)
        print(f"{len(df)} registros lidos do banco.")
        return df

    except SQLAlchemyError as e:
        print(f"Erro ao ler do banco de dados: {e}")
        return pd.DataFrame()


if __name__ == "__main__":
    from fetch_data import fetch_stock_data
    from transform_data import transform_stock_data

    raw_df = fetch_stock_data()
    transformed_df = transform_stock_data(raw_df)
    load_to_postgres(transformed_df)