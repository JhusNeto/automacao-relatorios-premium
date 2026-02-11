"""
Módulo de Visualização e Relatório PDF.
Gera dashboard PDF com gráficos, tabelas e KPIs. Design corporativo:
azul escuro + cinza + branco, títulos nítidos, cards de KPI, sumário.
"""
import io
import logging
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image,
    PageBreak, ListFlowable, ListItem,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

logger = logging.getLogger(__name__)

# Paleta: azul escuro, cinza, branco
COR_TITULO = colors.HexColor("#1e3a5f")
COR_SUBTITULO = colors.HexColor("#4a6fa5")
COR_TEXTO = colors.HexColor("#333333")
COR_CINZA = colors.HexColor("#6b7280")
COR_FUNDO_CARD = colors.HexColor("#f3f4f6")
COR_BORDA = colors.HexColor("#e5e7eb")


def _fig_to_image(fig: plt.Figure, width_cm: float = 16) -> Image:
    """Converte matplotlib Figure em Image do ReportLab."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120, bbox_inches="tight", facecolor="white")
    buf.seek(0)
    img = Image(buf, width=width_cm * cm, height=(width_cm * 0.6) * cm)
    plt.close(fig)
    return img


def _grafico_barras_categoria(df: pd.DataFrame, titulo: str = "Total por Categoria") -> Image:
    """Gráfico de barras horizontais para totais por categoria."""
    if df.empty or "categoria" not in df.columns or "total" not in df.columns:
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.text(0.5, 0.5, "Sem dados", ha="center", va="center", fontsize=12)
        return _fig_to_image(fig, width_cm=14)
    df = df.head(12)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.barh(df["categoria"].astype(str)[::-1], df["total"][::-1], color="#1e3a5f", edgecolor="#e5e7eb", linewidth=0.5)
    ax.set_xlabel("Total", fontsize=9, color="#333333")
    ax.set_title(titulo, fontsize=11, fontweight="bold", color="#1e3a5f")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    return _fig_to_image(fig, width_cm=14)


def _grafico_evolucao(df: pd.DataFrame, titulo: str = "Evolução Mensal") -> Image:
    """Gráfico de linha para evolução mensal."""
    if df.empty or "mes_ano" not in df.columns or "total" not in df.columns:
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.text(0.5, 0.5, "Sem dados", ha="center", va="center", fontsize=12)
        return _fig_to_image(fig, width_cm=14)
    fig, ax = plt.subplots(figsize=(6, 3.5))
    x = range(len(df))
    ax.plot(x, df["total"], color="#1e3a5f", marker="o", markersize=4, linewidth=2)
    ax.fill_between(x, df["total"], alpha=0.2, color="#1e3a5f")
    ax.set_xticks(x)
    ax.set_xticklabels(df["mes_ano"], rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("Total", fontsize=9, color="#333333")
    ax.set_title(titulo, fontsize=11, fontweight="bold", color="#1e3a5f")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    return _fig_to_image(fig, width_cm=14)


def _grafico_pizza_percentual(df: pd.DataFrame, titulo: str = "Distribuição %") -> Image:
    """Gráfico de pizza para percentual por grupo."""
    if df.empty or "categoria" not in df.columns or "percentual" not in df.columns:
        fig, ax = plt.subplots(figsize=(4, 4))
        ax.text(0.5, 0.5, "Sem dados", ha="center", va="center", fontsize=12)
        return _fig_to_image(fig, width_cm=10)
    df = df.head(8)
    fig, ax = plt.subplots(figsize=(4, 4))
    cores = plt.cm.Blues([0.3 + 0.6 * i / max(len(df), 1) for i in range(len(df))])
    ax.pie(df["percentual"], labels=df["categoria"].astype(str), autopct="%1.1f%%", colors=cores, startangle=90)
    ax.set_title(titulo, fontsize=11, fontweight="bold", color="#1e3a5f")
    fig.tight_layout()
    return _fig_to_image(fig, width_cm=10)


def gerar_pdf(metricas: dict[str, Any], caminho_saida: str | Path) -> None:
    """
    Gera PDF com sumário, KPIs em cards, tabelas e gráficos.
    Layout: capa/título, sumário, KPIs, gráficos, tabela de categorias.
    """
    caminho_saida = Path(caminho_saida)
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(caminho_saida),
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.2 * cm,
        bottomMargin=1.2 * cm,
    )
    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle(
        name="TituloPremium",
        parent=styles["Heading1"],
        fontSize=18,
        textColor=COR_TITULO,
        spaceAfter=6,
        alignment=TA_LEFT,
    )
    h2_style = ParagraphStyle(
        name="H2Premium",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=COR_SUBTITULO,
        spaceAfter=8,
        spaceBefore=12,
    )
    normal_style = ParagraphStyle(
        name="NormalPremium",
        parent=styles["Normal"],
        fontSize=10,
        textColor=COR_TEXTO,
        spaceAfter=6,
    )

    story = []

    # Título e introdução
    story.append(Paragraph("Relatório Automatizado", titulo_style))
    story.append(Paragraph("Dashboard gerado automaticamente a partir dos dados de entrada.", normal_style))
    story.append(Spacer(1, 0.5 * cm))

    # Sumário
    story.append(Paragraph("Sumário", h2_style))
    story.append(ListFlowable([
        ListItem(Paragraph("Resumo e KPIs", normal_style)),
        ListItem(Paragraph("Total por categoria", normal_style)),
        ListItem(Paragraph("Evolução mensal", normal_style)),
        ListItem(Paragraph("Distribuição percentual", normal_style)),
        ListItem(Paragraph("Tabela detalhada", normal_style)),
    ]))
    story.append(Spacer(1, 0.8 * cm))

    # KPIs em cards (tabela 2x2)
    story.append(Paragraph("Resumo e KPIs", h2_style))
    total = metricas.get("total_geral", 0)
    qtd = metricas.get("quantidade_registros", 0)
    media = metricas.get("media_geral", 0)
    kpi_data = [
        ["Total Geral", f"R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")],
        ["Registros", str(qtd)],
        ["Média", f"R$ {media:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")],
    ]
    t_kpi = Table(kpi_data, colWidths=[6 * cm, 6 * cm])
    t_kpi.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COR_FUNDO_CARD),
        ("TEXTCOLOR", (0, 0), (0, -1), COR_TEXTO),
        ("TEXTCOLOR", (1, 0), (1, -1), COR_TITULO),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOX", (0, 0), (-1, -1), 0.5, COR_BORDA),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, COR_BORDA),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(t_kpi)
    story.append(Spacer(1, 0.8 * cm))

    # Gráfico Total por Categoria
    story.append(Paragraph("Total por Categoria", h2_style))
    tot_cat = metricas.get("total_por_categoria", pd.DataFrame())
    story.append(_grafico_barras_categoria(tot_cat))
    story.append(Spacer(1, 0.5 * cm))

    # Gráfico Evolução Mensal
    story.append(Paragraph("Evolução Mensal", h2_style))
    evol = metricas.get("evolucao_mensal", pd.DataFrame())
    story.append(_grafico_evolucao(evol))
    story.append(Spacer(1, 0.5 * cm))

    # Gráfico Distribuição %
    story.append(Paragraph("Distribuição Percentual", h2_style))
    story.append(_grafico_pizza_percentual(tot_cat))
    story.append(Spacer(1, 0.5 * cm))

    # Tabela detalhada
    story.append(Paragraph("Tabela Detalhada por Categoria", h2_style))
    if not tot_cat.empty:
        tot_cat_copy = tot_cat.copy()
        tot_cat_copy["total"] = tot_cat_copy["total"].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        if "percentual" in tot_cat_copy.columns:
            tot_cat_copy["percentual"] = tot_cat_copy["percentual"].apply(lambda x: f"{x}%")
        table_data = [tot_cat_copy.columns.tolist()] + tot_cat_copy.head(15).values.tolist()
        t = Table(table_data, colWidths=[8 * cm, 4 * cm, 3 * cm] if len(tot_cat_copy.columns) >= 3 else [8 * cm, 5 * cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), COR_TITULO),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ALIGN", (0, 0), (0, -1), "LEFT"),
            ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
            ("BOX", (0, 0), (-1, -1), 0.5, COR_BORDA),
            ("INNERGRID", (0, 0), (-1, -1), 0.25, COR_BORDA),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COR_FUNDO_CARD]),
        ]))
        story.append(t)
    else:
        story.append(Paragraph("Nenhum dado disponível para exibir.", normal_style))

    doc.build(story)
    logger.info("PDF gerado: %s", caminho_saida)
