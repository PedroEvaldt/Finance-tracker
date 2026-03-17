"""Categorização de transações com base em regras externas (YAML)."""

import re
from pathlib import Path

import pandas as pd
import yaml

DEFAULT_CONFIG = Path(__file__).parent.parent / "config" / "categories.yaml"
DEFAULT_OVERRIDES = Path(__file__).parent.parent / "data" / "output" / "category_overrides.csv"


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


def apply_overrides(df: pd.DataFrame, overrides_path: Path = DEFAULT_OVERRIDES) -> pd.DataFrame:
    """Aplica correções manuais de categoria salvas pelo dashboard."""
    if not overrides_path.exists():
        return df
    overrides = pd.read_csv(overrides_path)
    if overrides.empty:
        return df
    df = df.copy()
    override_map = overrides.set_index("identificador")["categoria"].to_dict()
    mask = df["identificador"].isin(override_map)
    df.loc[mask, "categoria"] = df.loc[mask, "identificador"].map(override_map)
    df.loc[mask, "confianca_categoria"] = "manual"
    df.loc[mask, "revisao_manual"] = False
    return df
