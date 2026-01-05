# Pipeline ETL com Python + IA

Projeto de portfólio replicando um fluxo **ETL (Extract, Transform, Load)**.

## Fluxo
- **Extract:** lê dados de `data/users.csv` (offline) ou IDs em `data/SDW2023.csv`
- **Transform:** gera mensagens personalizadas com IA (OpenAI)
- **Load:** salva em `output/users_enriched.json` e `output/messages.csv`

## Como executar
1. Instale dependências:
```bash
pip install -r requirements.txt

