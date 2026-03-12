"""Categorização de transações com base em regras externas (YAML)."""

import re
from pathlib import Path

import pandas as pd
import yaml

DEFAULT_CONFIG = Path(__file__).parent.parent / "config" / "categories.yaml"


def categorize(df: pd.DataFrame, config_path: Path = DEFAULT_CONFIG) -> pd.DataFrame:
    """Aplica regras de categorização ao DataFrame enriquecido."""
    rules = _load_rules(config_path)
    df = df.copy()
    df[["categoria", "confianca_categoria"]] = df["descricao_normalizada"].apply(
        lambda desc: pd.Series(_classify(desc, rules))
    )
    df["revisao_manual"] = df["confianca_categoria"] == "baixa"
    return df


def _load_rules(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Arquivo de categorias não encontrado: {path}")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _classify(descricao: str, rules: dict) -> tuple[str, str]:
    """Retorna (categoria, confianca). Confiança: 'alta' ou 'baixa'."""
    for categoria, keywords in rules.items():
        for keyword in keywords:
            if re.search(str(keyword), descricao, re.IGNORECASE):
                return categoria, "alta"
    return "outros", "baixa"
