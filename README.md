# Finance Tracker — Nubank

Aplicação Python para processar extratos CSV exportados da Nubank, categorizar transações e visualizar análises financeiras via dashboard interativo.

## Funcionalidades

- Leitura e validação de arquivos CSV da Nubank
- Limpeza e normalização de dados (datas, valores, descrições)
- Categorização automática por regras configuráveis em YAML
- Suporte a múltiplos meses simultaneamente
- Dashboard interativo com filtros, gráficos e edição manual de categorias
- Exportação dos dados processados em CSV

## Requisitos

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (gerenciador de pacotes)

## Instalação

```bash
git clone <url-do-repositorio>
cd finance_tracker
uv sync
```

## Como usar

### 1. Adicionar os extratos

Copie os arquivos CSV exportados da Nubank para `data/input/`.

No app da Nubank: **Minha Conta → Extrato → Exportar**.

### 2. Rodar o pipeline

```bash
# Processar todos os CSVs da pasta de uma vez (recomendado)
python main.py data/input/

# Ou arquivos específicos
python main.py data/input/extrato_jan.csv data/input/extrato_fev.csv
```

Os arquivos gerados ficam em `data/output/`:

| Arquivo | Conteúdo |
|---|---|
| `transactions_cleaned.csv` | Transações limpas e normalizadas |
| `transactions_categorized.csv` | Transações com categorias e colunas derivadas |
| `category_summary.csv` | Total de gastos por categoria |
| `monthly_summary.csv` | Receita e despesa por mês |
| `review_needed.csv` | Transações com baixa confiança na categorização |

### 3. Abrir o dashboard

```bash
streamlit run app/dashboard.py
```

O dashboard oferece:
- Métricas de receita, despesas e saldo do período
- Filtro por mês na barra lateral
- Gráfico de pizza com distribuição por categoria
- Gráfico de receita vs despesa por mês
- Ranking dos estabelecimentos com mais gastos
- Tabela editável para corrigir categorias manualmente

### 4. Corrigir categorias manualmente

Na seção **"Todas as transações"** do dashboard, clique na coluna **Categoria** de qualquer linha e selecione a categoria correta. A correção é salva automaticamente em `data/output/category_overrides.csv` e aplicada nas próximas execuções do pipeline.

## Configuração de categorias

As regras de categorização ficam em `config/categories.yaml`. A ordem das categorias importa — a primeira que casar com a descrição da transação vence.

```yaml
alimentacao:
  - ifood
  - kampeki
  - restaurante
  - lancheria

transporte:
  - uber
  - taxi
```

As palavras-chave são comparadas contra a descrição normalizada (sem acentos, em minúsculas). Transações sem match ficam como `outros` e são marcadas para revisão manual.

## Estrutura do projeto

```
finance_tracker/
├── finance_tracker/       # Módulos principais
│   ├── ingestion.py       # Leitura e validação de CSVs
│   ├── cleaning.py        # Limpeza e normalização
│   ├── enrichment.py      # Colunas derivadas (mês, tipo, estabelecimento)
│   ├── categorization.py  # Categorização por regras + overrides
│   ├── analysis.py        # Resumos analíticos
│   └── export.py          # Exportação para CSV
├── app/
│   └── dashboard.py       # Dashboard Streamlit
├── config/
│   └── categories.yaml    # Regras de categorização
├── data/
│   ├── input/             # CSVs da Nubank (não versionados)
│   └── output/            # Arquivos gerados pelo pipeline (não versionados)
├── tests/                 # Testes automatizados
└── main.py                # Entrypoint do pipeline
```

## Testes

```bash
python -m pytest
```
