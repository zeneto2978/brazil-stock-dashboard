# 📊 Brazil Stock Dashboard

Projeto de **Engenharia de Dados** com dados da bolsa brasileira (B3), incluindo pipeline ETL completo e dashboard interativo.

---

## 🚀 Visão Geral

Este projeto demonstra a construção de um pipeline de dados de ponta a ponta:

* 📥 Ingestão de dados de mercado (API)
* 🔄 Transformação com Pandas
* 🗄️ Armazenamento em PostgreSQL
* 📊 Visualização com Streamlit

---

## 🖼️ Preview do Dashboard

### 📈 Visão Geral

![Dashboard](./images/dashboard.png)

### 📊 Gráfico com Médias Móveis

![Chart](./images/chart.png)

> 💡 *Adicione screenshots reais depois para deixar o projeto ainda mais profissional*

---

## ⚙️ Funcionalidades

* Coleta de dados de ações brasileiras (PETR4, VALE3, ITUB4)
* Cálculo de indicadores:

  * Média móvel (MA9)
  * Média móvel (MA21)
* Classificação de tendência:

  * 📈 Alta
  * 📉 Baixa
* Dashboard interativo
* Filtro por ativo
* Visualização de histórico de preços

---

## 🧱 Arquitetura do Projeto

```
API (Brapi)
   ↓
Ingestão (fetch_data.py)
   ↓
Transformação (transform_data.py)
   ↓
PostgreSQL (stock_prices)
   ↓
Streamlit Dashboard
```

---

## 🛠️ Tecnologias Utilizadas

* Python
* Pandas
* PostgreSQL
* SQLAlchemy
* Streamlit

---

## 📂 Estrutura do Projeto

```
brazil-stock-dashboard/
│
├── app/
│   └── dashboard.py
│
├── scripts/
│   ├── fetch_data.py
│   ├── transform_data.py
│   └── load_data.py
│
├── config/
│   └── settings.py
│
├── sql/
│   └── create_tables.sql
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## ▶️ Como Executar

### 1. Criar ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Criar banco PostgreSQL

```sql
CREATE DATABASE stocks_db;
```

### 4. Executar pipeline

```bash
PYTHONPATH=. python scripts/load_data.py
```

### 5. Rodar dashboard

```bash
PYTHONPATH=. streamlit run app/dashboard.py
```

---

## ⚠️ Observações

* Os dados podem apresentar diferenças em relação a outras plataformas devido a:

  * atraso de mercado
  * fonte de dados
  * horário de atualização
  * arredondamento

---

## 💡 Próximas melhorias

* Simulador de trading DEMO
* Gráficos com Plotly
* Deploy online (Streamlit Cloud)
* Atualização automática de dados
* Mais indicadores técnicos

---

## 👨‍💻 Autor

Projeto desenvolvido como parte do aprendizado em **Engenharia de Dados**.
