#!/usr/bin/env python3
"""
Projeto Premium #1 — Automação de Relatórios

Uso:
  1. Coloque arquivos Excel na pasta input/
  2. Execute: python main.py
  3. PDFs serão gerados na pasta output/ (com timestamp no nome)

Modo único arquivo:
  python main.py input/meu_arquivo.xlsx

Modo monitoramento (processa novos arquivos automaticamente):
  python main.py --watch
"""
import argparse
import logging
import sys
from pathlib import Path

# Garante que src está no path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.ingestao import ler_excel, validar_colunas_esperadas
from src.tratamento import limpar_duplicados, padronizar_datas, criar_metricas
from src.relatorio_pdf import gerar_pdf
from src.automacao import processar_arquivo, nome_saida_com_timestamp, iniciar_monitoramento

# Configuração de logs: simples e claros
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

INPUT_DIR = Path(__file__).resolve().parent / "input"
OUTPUT_DIR = Path(__file__).resolve().parent / "output"


def processar(caminho_excel: Path, pasta_saida: Path | None = None) -> Path | None:
    """
    Fluxo completo: ingestão -> tratamento -> métricas -> PDF.
    Retorna o path do PDF gerado ou None em caso de erro.
    """
    pasta_saida = pasta_saida or OUTPUT_DIR
    try:
        logger.info("Processando: %s", caminho_excel)
        df = ler_excel(caminho_excel)
        validar_colunas_esperadas(df)
        df = limpar_duplicados(df)
        df = padronizar_datas(df)
        metricas = criar_metricas(df)
        pasta_saida.mkdir(parents=True, exist_ok=True)
        nome_pdf = nome_saida_com_timestamp()
        caminho_pdf = pasta_saida / nome_pdf
        gerar_pdf(metricas, caminho_pdf)
        logger.info("Relatório gerado: %s", caminho_pdf)
        return caminho_pdf
    except FileNotFoundError as e:
        logger.error("Arquivo não encontrado: %s", e)
        return None
    except ValueError as e:
        logger.error("Dados inválidos: %s", e)
        return None
    except Exception as e:
        logger.exception("Erro ao processar: %s", e)
        return None


def main():
    parser = argparse.ArgumentParser(description="Automação de Relatórios — gera PDF a partir de Excel")
    parser.add_argument(
        "entrada",
        nargs="?",
        default=None,
        help="Caminho do arquivo Excel ou pasta input/ (padrão: processa o primeiro .xlsx em input/)",
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Monitora a pasta input/ e gera relatório a cada novo arquivo",
    )
    parser.add_argument(
        "--output-dir",
        default=OUTPUT_DIR,
        type=Path,
        help="Pasta de saída dos PDFs (padrão: output/)",
    )
    args = parser.parse_args()
    out_dir = Path(args.output_dir)

    if args.watch:
        INPUT_DIR.mkdir(parents=True, exist_ok=True)
        observer = iniciar_monitoramento(INPUT_DIR, out_dir, lambda p: processar(p, out_dir))
        logger.info("Aguardando novos arquivos em %s. Pressione Ctrl+C para encerrar.", INPUT_DIR)
        try:
            observer.join()
        except KeyboardInterrupt:
            observer.stop()
            observer.join()
        return

    # Modo único: arquivo ou pasta
    if args.entrada:
        entrada = Path(args.entrada)
        if entrada.is_file():
            out = processar(entrada, out_dir)
            sys.exit(0 if out else 1)
        if entrada.is_dir():
            xlsx = list(entrada.glob("*.xlsx")) or list(entrada.glob("*.xls"))
            if not xlsx:
                logger.error("Nenhum arquivo .xlsx ou .xls encontrado em %s", entrada)
                sys.exit(1)
            for f in xlsx:
                processar(f, out_dir)
            return

    # Padrão: processa input/
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    arquivos = list(INPUT_DIR.glob("*.xlsx")) + list(INPUT_DIR.glob("*.xls"))
    if not arquivos:
        logger.info("Pasta input/ vazia. Coloque um arquivo Excel em input/ e execute novamente.")
        logger.info("Exemplo: cp sample_input.xlsx input/ && python main.py")
        sys.exit(0)
    for arq in arquivos:
        processar(arq, out_dir)


if __name__ == "__main__":
    main()
