"""Configurações centrais de caminhos e ferramentas do video_scrapper."""

import os
import re
import shutil
import unicodedata
from pathlib import Path

from dotenv import load_dotenv

# Raiz do projeto: independente do diretório de onde o comando é executado.
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# FFmpeg: LOCAL usa executável dentro do projeto; PATH usa instalação do sistema.
FFMPEG_MODE = os.getenv("FFMPEG_MODE", "PATH").upper()
FFMPEG_LOCAL_PATH = os.getenv("FFMPEG_LOCAL_PATH", "bin/ffmpeg.exe")


def obter_ffmpeg() -> Path:
    """Resolve o executável do FFmpeg conforme .env."""
    if FFMPEG_MODE == "LOCAL":
        caminho = Path(FFMPEG_LOCAL_PATH)
        if not caminho.is_absolute():
            caminho = BASE_DIR / caminho
        if not caminho.is_file():
            raise FileNotFoundError(f"FFmpeg local não encontrado: {caminho}")
        return caminho
    if FFMPEG_MODE == "PATH":
        caminho = shutil.which("ffmpeg")
        if caminho is None:
            raise FileNotFoundError(
                "FFmpeg não encontrado no PATH. Instale-o ou configure FFMPEG_MODE=LOCAL no .env."
            )
        return Path(caminho)
    raise ValueError(f"FFMPEG_MODE inválido: {FFMPEG_MODE}. Use LOCAL ou PATH.")


FFMPEG_PATH = obter_ffmpeg()

# Diretórios de entrada e saída
VIDEOS_DIR = BASE_DIR / "videos"
AUDIOS_DIR = BASE_DIR / "audios"
TRANSCRICOES_DIR = BASE_DIR / "transcricoes"
RANK_DIR = BASE_DIR / "rankeamento"
FRAMES_DIR = BASE_DIR / "video_frames"
VISUAIS_DIR = BASE_DIR / "transcricoes_visuais"
MODELS_DIR = BASE_DIR / "models"

# Modelo semântico baixado por hugger.py
SEMANTIC_MODEL_ID = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
SEMANTIC_MODEL_DIR = MODELS_DIR / "paraphrase-multilingual-MiniLM-L12-v2"

# Tesseract OCR. Pode ser um caminho absoluto ou relativo à raiz do projeto.
TESSERACT_CMD = os.getenv("TESSERACT_CMD", "")
TESSERACT_LOCAL_PATH = BASE_DIR / "bin" / "Tesseract-OCR" / "tesseract.exe"


def nome_seguro(nome: str) -> str:
    """Converte um nome em um formato seguro para arquivos no Windows."""
    nome = unicodedata.normalize("NFKD", nome)
    nome = "".join(c for c in nome if not unicodedata.combining(c))
    nome = re.sub(r'[<>:"/\\|?*]', "", nome)
    nome = re.sub(r"\s+", "_", nome)
    nome = nome.rstrip(". ")
    return nome or "arquivo_sem_nome"
