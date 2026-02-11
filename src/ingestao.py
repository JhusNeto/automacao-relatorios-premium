"""
Módulo de Ingestão - Lê Excel em múltiplos formatos.
Detecta abas, colunas e inconsistências. Normaliza nomes e tipos.
"""
import re
import logging
from pathlib import Path
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)

# Mapeamento comum de nomes de colunas para normalização
COLUNA_ALIASES = {
    "data": ["data", "date", "dt", "data_emissao", "emissao"],
    "categoria": ["categoria", "category", "tipo", "grupo", "segmento"],
    "valor": ["valor", "value", "valor_total", "total", "venda", "receita", "valor_venda"],
    "quantidade": ["quantidade", "qtd", "qty", "quant", "volume"],
    "produto": ["produto", "product", "item", "descricao", "nome"],
    "regiao": ["regiao", "region", "estado", "uf", "cidade", "filial"],
}


def _normalizar_nome_coluna(nome: str) -> str:
    """Remove acentos, espaços extras e padroniza para minúsculo."""
    if not isinstance(nome, str) or pd.isna(nome):
        return "coluna_desconhecida"
    n = nome.strip().lower()
    n = re.sub(r"\s+", "_", n)
    # Remove caracteres especiais mantendo underscore
    n = re.sub(r"[^a-z0-9_]", "", n)
    return n or "coluna_desconhecida"


def _identificar_coluna_canonica(nome_normalizado: str) -> str | None:
    """Retorna o nome canônico da coluna se existir no mapeamento."""
    for canonico, aliases in COLUNA_ALIASES.items():
        if nome_normalizado in aliases or nome_normalizado.replace("_", "") in [a.replace("_", "") for a in aliases]:
            return canonico
    return None


def _inferir_tipo(series: pd.Series) -> str:
    """Infere tipo: data, numero, texto."""
    if series.empty:
        return "texto"
    # Tenta converter para numérico
    try:
        pd.to_numeric(series.dropna().astype(str).str.replace(",", ".", regex=False), errors="coerce")
        if pd.to_numeric(series.dropna().astype(str).str.replace(",", ".", regex=False), errors="coerce").notna().any():
            return "numero"
    except Exception:
        pass
    # Tenta converter para data
    try:
        pd.to_datetime(series.dropna(), errors="coerce")
        if pd.to_datetime(series.dropna(), errors="coerce").notna().any():
            return "data"
    except Exception:
        pass
    return "texto"


def ler_excel(caminho: str | Path) -> pd.DataFrame:
    """
    Lê arquivo Excel. Tenta todas as abas e concatena ou usa a primeira com dados.
    Detecta abas, normaliza colunas e identifica tipos.
    """
    caminho = Path(caminho)
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

    try:
        xl = pd.ExcelFile(caminho, engine="openpyxl")
    except Exception as e:
        raise ValueError(f"Não foi possível abrir o Excel: {e}") from e

    sheets = xl.sheet_names
    if not sheets:
        raise ValueError("O arquivo Excel não contém abas.")

    # Tenta ler a primeira aba com mais de uma linha
    df = None
    for sheet in sheets:
        try:
            d = pd.read_excel(xl, sheet_name=sheet, header=0)
            if d.shape[0] >= 1 and d.shape[1] >= 1:
                df = d
                logger.info("Usando aba: %s", sheet)
                break
        except Exception as e:
            logger.warning("Aba %s ignorada: %s", sheet, e)
            continue

    if df is None or df.empty:
        raise ValueError("Nenhuma aba do Excel contém dados utilizáveis.")

    # Normalizar nomes das colunas
    df.columns = [_normalizar_nome_coluna(str(c)) for c in df.columns]
    # Colunas duplicadas: sufixo _1, _2...
    seen: dict[str, int] = {}
    new_columns = []
    for c in df.columns:
        if c in seen:
            seen[c] += 1
            new_columns.append(f"{c}_{seen[c]}")
        else:
            seen[c] = 0
            new_columns.append(c)
    df.columns = new_columns

    # Identificar tipos por coluna
    for col in df.columns:
        tipo = _inferir_tipo(df[col])
        if tipo == "numero":
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", ".", regex=False), errors="coerce")
        elif tipo == "data":
            df[col] = pd.to_datetime(df[col], errors="coerce")

    logger.info("Ingestão concluída: %d linhas, %d colunas", len(df), len(df.columns))
    return df


def validar_colunas_esperadas(df: pd.DataFrame, colunas_minimas: list[str] | None = None) -> None:
    """
    Valida se há pelo menos uma coluna numérica e uma para agrupamento.
    Opcionalmente exige colunas mínimas por nome canônico.
    """
    if df.empty:
        raise ValueError("DataFrame vazio após ingestão.")
    numericas = df.select_dtypes(include=["number"]).columns.tolist()
    if not numericas:
        raise ValueError(
            "Nenhuma coluna numérica detectada. O relatório precisa de pelo menos uma coluna de valores."
        )
    if colunas_minimas:
        for c in colunas_minimas:
            if c not in df.columns and not any(_identificar_coluna_canonica(col) == c for col in df.columns):
                raise ValueError(f"Coluna esperada não encontrada: {c}")
