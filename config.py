import os
import shutil
import re
import unicodedata

from pathlib import Path

from dotenv import load_dotenv


# Diretório raiz do projeto
BASE_DIR = Path(__file__).resolve().parent


# Carrega o .env
load_dotenv(BASE_DIR / ".env")


# ==========================================
# CONFIGURAÇÃO DO FFMPEG
# ==========================================

FFMPEG_MODE = os.getenv("FFMPEG_MODE", "PATH").upper()

FFMPEG_LOCAL_PATH = os.getenv(
    "FFMPEG_LOCAL_PATH",
    "bin/ffmpeg.exe"
)


def obter_ffmpeg() -> Path:
    """
    Retorna o caminho do executável FFmpeg
    de acordo com a configuração do .env.
    """

    # --------------------------------------
    # FFmpeg local
    # --------------------------------------

    if FFMPEG_MODE == "LOCAL":

        caminho = BASE_DIR / FFMPEG_LOCAL_PATH

        if not caminho.exists():
            raise FileNotFoundError(
                f"FFmpeg local não encontrado: {caminho}"
            )

        return caminho


    # --------------------------------------
    # FFmpeg instalado na máquina
    # --------------------------------------

    if FFMPEG_MODE == "PATH":

        caminho = shutil.which("ffmpeg")

        if caminho is None:
            raise FileNotFoundError(
                "FFmpeg não encontrado no PATH da máquina."
            )

        return Path(caminho)


    # --------------------------------------
    # Configuração inválida
    # --------------------------------------

    raise ValueError(
        f"FFMPEG_MODE inválido: {FFMPEG_MODE}. "
        "Use LOCAL ou PATH."
    )


FFMPEG_PATH = obter_ffmpeg()

VIDEOS_DIR = BASE_DIR / "videos"
AUDIOS_DIR = BASE_DIR / "audios"
TRANSCRICOES_DIR = BASE_DIR / "transcricoes"


def nome_seguro(nome: str) -> str:
    """
    Converte um nome em um formato seguro para arquivos no Windows.
    """

    # Remove acentos
    nome = unicodedata.normalize("NFKD", nome)
    nome = "".join(
        caractere
        for caractere in nome
        if not unicodedata.combining(caractere)
    )

    # Remove caracteres proibidos pelo Windows
    nome = re.sub(r'[<>:"/\\|?*]', "", nome)

    # Substitui espaços consecutivos por "_"
    nome = re.sub(r"\s+", "_", nome)

    # Remove pontos e espaços no final
    nome = nome.rstrip(". ")

    # Evita nome vazio
    if not nome:
        nome = "arquivo_sem_nome"

    return nome