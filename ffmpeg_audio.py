"""Extração do áudio de vídeos usando FFmpeg."""

import subprocess
from pathlib import Path

from config import AUDIOS_DIR, FFMPEG_PATH


def verificar_ffmpeg():
    if not FFMPEG_PATH.is_file():
        raise RuntimeError(f"FFmpeg não encontrado ou inválido: {FFMPEG_PATH}")


def extrair_audio(video: Path):
    if not video.exists():
        raise FileNotFoundError(f"Vídeo não encontrado: {video}")
    if not video.is_file():
        raise FileNotFoundError(f"O caminho informado não é um arquivo: {video}")

    verificar_ffmpeg()
    AUDIOS_DIR.mkdir(parents=True, exist_ok=True)
    saida = AUDIOS_DIR / f"{video.stem}.mp3"

    print(f"Vídeo: {video}")
    print(f"Saída: {saida}")
    print("Extraindo áudio...")
    comando = [str(FFMPEG_PATH), "-i", str(video), "-vn", "-y", str(saida)]
    resultado = subprocess.run(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if resultado.returncode != 0:
        raise RuntimeError(f"Erro durante a execução do FFmpeg:\\n{resultado.stderr}")
    print("Áudio extraído com sucesso!")
    return saida
