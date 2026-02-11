"""
Módulo de Automação.
Monitora pasta de entrada, gera relatórios ao detectar novos arquivos,
salva com timestamp. Opcional: envio por e-mail ou webhook.
"""
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Callable

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

logger = logging.getLogger(__name__)


def nome_saida_com_timestamp() -> str:
    """Retorna nome de arquivo com timestamp para unicidade."""
    return f"relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"


def processar_arquivo(caminho_entrada: Path, pasta_saida: Path, processador: Callable) -> Path | None:
    """
    Processa um arquivo Excel e gera PDF na pasta de saída com timestamp.
    processador: função que recebe (path_excel) e retorna (path_pdf) ou None.
    """
    if not caminho_entrada.exists():
        logger.error("Arquivo não encontrado: %s", caminho_entrada)
        return None
    try:
        out = processador(caminho_entrada)
        if out and Path(out).exists():
            out_path = Path(out)
            if out_path.parent.resolve() != pasta_saida.resolve():
                dest = pasta_saida / nome_saida_com_timestamp()
                out_path.rename(dest)
                logger.info("Relatório salvo: %s", dest)
                return dest
            logger.info("Relatório salvo: %s", out_path)
            return out_path
    except Exception as e:
        logger.exception("Erro ao processar %s: %s", caminho_entrada, e)
    return None


class HandlerNovoExcel(FileSystemEventHandler):
    """Handler que reage a novos arquivos .xlsx na pasta monitorada."""

    def __init__(self, pasta_saida: Path, processador: Callable):
        self.pasta_saida = Path(pasta_saida)
        self.processador = processador
        self.pasta_saida.mkdir(parents=True, exist_ok=True)

    def on_created(self, event: FileCreatedEvent):
        if event.is_directory:
            return
        path = Path(event.src_path)
        if path.suffix.lower() in (".xlsx", ".xls"):
            logger.info("Novo arquivo detectado: %s", path)
            time.sleep(0.5)  # Garantir que o arquivo foi totalmente escrito
            processar_arquivo(path, self.pasta_saida, self.processador)


def iniciar_monitoramento(
    pasta_entrada: str | Path,
    pasta_saida: str | Path,
    processador: Callable,
) -> Observer:
    """
    Inicia monitoramento da pasta. Novos Excel geram PDF em pasta_saida com timestamp.
    Retorna o Observer; use observer.join() para bloquear.
    """
    pasta_entrada = Path(pasta_entrada)
    pasta_saida = Path(pasta_saida)
    pasta_entrada.mkdir(parents=True, exist_ok=True)
    pasta_saida.mkdir(parents=True, exist_ok=True)

    observer = Observer()
    handler = HandlerNovoExcel(pasta_saida, processador)
    observer.schedule(handler, str(pasta_entrada), recursive=False)
    observer.start()
    logger.info("Monitoramento ativo: %s -> %s", pasta_entrada, pasta_saida)
    return observer
