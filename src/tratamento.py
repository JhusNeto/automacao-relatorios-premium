"""
Módulo de Tratamento e Enriquecimento.
Limpeza, padronização e criação de métricas genéricas (total por categoria,
ticket médio, evolução mês a mês, percentual por grupo).
"""
import logging
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


def limpar_duplicados(df: pd.DataFrame, subset: list[str] | None = None) -> pd.DataFrame:
    """Remove linhas duplicadas. Se subset for None, usa todas as colunas."""
    antes = len(df)
    df = df.drop_duplicates(subset=subset).reset_index(drop=True)
    logger.info("Duplicados removidos: %d linhas", antes - len(df))
    return df


def padronizar_datas(df: pd.DataFrame, colunas_data: list[str] | None = None) -> pd.DataFrame:
    """Padroniza colunas de data para datetime e preenche falhas quando possível."""
    if colunas_data is None:
        colunas_data = [c for c in df.columns if df[c].dtype == "datetime64[ns]"]
    for col in colunas_data:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def texto_para_numero(df: pd.DataFrame, colunas: list[str] | None = None) -> pd.DataFrame:
    """Converte colunas de texto para numérico (usa vírgula/ponto como decimal)."""
    if colunas is None:
        colunas = df.select_dtypes(include=["object"]).columns.tolist()
    for col in colunas:
        if col not in df.columns:
            continue
        try:
            s = df[col].astype(str).str.replace(",", ".", regex=False)
            df[col] = pd.to_numeric(s, errors="coerce")
        except Exception as e:
            logger.warning("Coluna %s não convertida: %s", col, e)
    return df


def _coluna_valor(df: pd.DataFrame) -> str:
    """Identifica coluna principal de valor (numérica)."""
    numericas = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c]) and df[c].notna().any()]
    preferidas = ["valor", "valor_total", "total", "venda", "receita", "valor_venda"]
    for p in preferidas:
        for c in numericas:
            if p in c:
                return c
    return numericas[0] if numericas else ""


def _coluna_categoria(df: pd.DataFrame) -> str | None:
    """Identifica coluna de categoria/agrupamento (texto ou poucos valores únicos)."""
    candidatas = [c for c in df.columns if c not in ["data", "valor", "valor_total", "total"]]
    for nome in ["categoria", "tipo", "grupo", "segmento", "produto", "regiao", "estado", "uf"]:
        for c in candidatas:
            if nome in c and df[c].notna().any():
                return c
    for c in candidatas:
        if df[c].dtype == "object" or df[c].nunique() <= 50:
            return c
    return None


def _coluna_data(df: pd.DataFrame) -> str | None:
    """Identifica coluna de data."""
    for c in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[c]):
            return c
    for nome in ["data", "date", "dt", "emissao"]:
        for c in df.columns:
            if nome in c:
                return c
    return None


def criar_metricas(df: pd.DataFrame) -> dict[str, Any]:
    """
    Cria métricas genéricas para o relatório:
    - total_geral, total_por_categoria, ticket_medio
    - evolucao_mensal (se houver coluna de data)
    - percentual_por_grupo
    Retorna um dicionário com DataFrames e valores escalares para o PDF.
    """
    df = df.copy()
    col_valor = _coluna_valor(df)
    if not col_valor:
        raise ValueError("Nenhuma coluna numérica de valor encontrada para métricas.")

    metricas: dict[str, Any] = {}
    metricas["total_geral"] = float(df[col_valor].sum())
    metricas["quantidade_registros"] = int(len(df))
    metricas["media_geral"] = float(df[col_valor].mean()) if len(df) else 0.0

    col_cat = _coluna_categoria(df)
    if col_cat:
        tot_cat = df.groupby(col_cat, dropna=False)[col_valor].sum().reset_index()
        tot_cat.columns = ["categoria", "total"]
        tot_cat["percentual"] = (tot_cat["total"] / metricas["total_geral"] * 100).round(1)
        metricas["total_por_categoria"] = tot_cat.sort_values("total", ascending=False)
        metricas["ticket_medio_por_categoria"] = (
            df.groupby(col_cat, dropna=False)[col_valor].mean().reset_index()
        )
        metricas["percentual_por_grupo"] = tot_cat[["categoria", "percentual"]].to_dict("records")
    else:
        metricas["total_por_categoria"] = pd.DataFrame(columns=["categoria", "total", "percentual"])
        metricas["ticket_medio_por_categoria"] = pd.DataFrame()
        metricas["percentual_por_grupo"] = []

    col_data = _coluna_data(df)
    if col_data:
        df["_mes_ano"] = df[col_data].dt.to_period("M").astype(str)
        evol = df.groupby("_mes_ano", dropna=False)[col_valor].sum().reset_index()
        evol.columns = ["mes_ano", "total"]
        metricas["evolucao_mensal"] = evol.sort_values("mes_ano")
    else:
        metricas["evolucao_mensal"] = pd.DataFrame(columns=["mes_ano", "total"])

    logger.info("Métricas criadas: total_geral=%.2f, categorias=%d", metricas["total_geral"], len(metricas["total_por_categoria"]))
    return metricas
