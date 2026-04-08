# Brazil Stock Dashboard

Projeto de engenharia de dados com ações da bolsa brasileira (B3), usando pipeline ETL e dashboard interativo.

## Funcionalidades
- Coleta de dados de ações brasileiras via API
- Transformação de dados com Pandas
- Cálculo de médias móveis (MA9 e MA21)
- Classificação de tendência (Alta/Baixa)
- Armazenamento em PostgreSQL
- Dashboard interativo com Streamlit

## Tecnologias
- Python
- Pandas
- PostgreSQL
- SQLAlchemy
- Streamlit

## Estrutura do projeto
- `scripts/fetch_data.py` → coleta os dados
- `scripts/transform_data.py` → transforma os dados
- `scripts/load_data.py` → carrega no PostgreSQL
- `app/dashboard.py` → dashboard no Streamlit

## Como executar
```bash
pip install -r requirements.txt
PYTHONPATH=. python scripts/load_data.py
PYTHONPATH=. streamlit run app/dashboard.py