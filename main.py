"""Pipeline principal: ingestão → limpeza → enriquecimento → categorização → análise → exportação."""

import sys
from pathlib import Path

from finance_tracker import analysis, categorization, cleaning, enrichment, export, ingestion


def resolve_paths(args: list[str]) -> list[Path]:
    """Aceita um diretório ou uma lista de arquivos CSV."""
    if len(args) == 1 and Path(args[0]).is_dir():
        paths = sorted(Path(args[0]).glob("*.csv"))
        if not paths:
            raise FileNotFoundError(f"Nenhum CSV encontrado em: {args[0]}")
        return paths
    return [Path(p) for p in args]


def run(csv_paths: list[str | Path]) -> None:
    paths = resolve_paths([str(p) for p in csv_paths]) if isinstance(csv_paths, list) else resolve_paths([str(csv_paths)])

    print(f"Processando {len(paths)} arquivo(s):")
    for p in paths:
        print(f"  - {p}")

    df = ingestion.load_multiple_nubank_csvs(paths)
    df_clean = cleaning.clean(df)
    df = enrichment.enrich(df_clean)
    df = categorization.categorize(df)
    df = categorization.apply_overrides(df)

    cat_summary = analysis.summary_by_category(df)
    monthly_summary = analysis.summary_by_month(df)
    review = analysis.transactions_for_review(df)

    export.export_all(
        df_cleaned=df_clean,
        df_categorized=df,
        cat_summary=cat_summary,
        monthly_summary=monthly_summary,
        review=review,
    )
    print(f"Pipeline concluída: {len(df)} transações processadas.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python main.py data/input/          # todos os CSVs do diretório")
        print("  python main.py arquivo1.csv arquivo2.csv  # arquivos específicos")
        sys.exit(1)
    run(sys.argv[1:])
