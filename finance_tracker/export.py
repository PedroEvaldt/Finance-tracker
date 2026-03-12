"""Exportação dos DataFrames processados para CSV."""

from pathlib import Path

import pandas as pd

OUTPUT_DIR = Path(__file__).parent.parent / "data" / "output"


def export_all(
    df_cleaned: pd.DataFrame,
    df_categorized: pd.DataFrame,
    cat_summary: pd.DataFrame,
    monthly_summary: pd.DataFrame,
    review: pd.DataFrame,
    output_dir: Path = OUTPUT_DIR,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _save(df_cleaned, output_dir / "transactions_cleaned.csv")
    _save(df_categorized, output_dir / "transactions_categorized.csv")
    _save(cat_summary, output_dir / "category_summary.csv")
    _save(monthly_summary, output_dir / "monthly_summary.csv")
    _save(review, output_dir / "review_needed.csv")


def _save(df: pd.DataFrame, path: Path) -> None:
    df.to_csv(path, index=False, encoding="utf-8")
    print(f"Salvo: {path}")
