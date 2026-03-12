"""Pipeline principal: ingestão → limpeza → enriquecimento → categorização → análise → exportação."""

import sys
from pathlib import Path

from finance_tracker import analysis, categorization, cleaning, enrichment, export, ingestion


def run(csv_path: str | Path) -> None:
    print(f"Processando: {csv_path}")

    df = ingestion.load_nubank_csv(csv_path)
    df = cleaning.clean(df)
    df = enrichment.enrich(df)
    df = categorization.categorize(df)

    cat_summary = analysis.summary_by_category(df)
    monthly_summary = analysis.summary_by_month(df)
    review = analysis.transactions_for_review(df)

    # df_cleaned não tem colunas derivadas; exportamos a versão limpa antes do enrich
    df_cleaned = cleaning.clean(ingestion.load_nubank_csv(csv_path))

    export.export_all(
        df_cleaned=df_cleaned,
        df_categorized=df,
        cat_summary=cat_summary,
        monthly_summary=monthly_summary,
        review=review,
    )
    print("Pipeline concluída com sucesso.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python main.py <caminho_do_csv>")
        sys.exit(1)
    run(sys.argv[1])
