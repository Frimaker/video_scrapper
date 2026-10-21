"""Extração de frames nos timestamps selecionados pelo rankeamento semântico."""

import json
import subprocess
from pathlib import Path

from config import FFMPEG_PATH, FRAMES_DIR


def verificar_ffmpeg():
    if not FFMPEG_PATH.is_file():
        raise RuntimeError(f"FFmpeg não encontrado ou inválido: {FFMPEG_PATH}")


def rodar_comando(comando):
    resultado = subprocess.run(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if resultado.returncode != 0:
        raise RuntimeError(f"Erro durante a execução do FFmpeg:\\n{resultado.stderr}")


def get_frames(video_name: Path, local_transcricao: Path):
    verificar_ffmpeg()
    FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    video_frames_dir = FRAMES_DIR / video_name.stem
    video_frames_dir.mkdir(parents=True, exist_ok=True)

    with open(local_transcricao, "r", encoding="utf-8") as file:
        queries = json.load(file)

    for idq, q in enumerate(queries):
        query = queries[idq]["segmentos"]
        frase = queries[idq]["frase"]
        tempo_format = []
        for idt, t in enumerate(query):
            print(idt, t)
            tempo = query[idt]["Tempo"]
            print("timestamps: " + tempo)
            tempo_format.append(tempo)
            tempo_format[idt] = tempo_format[idt].replace(":", ".")
            print("FORMAT: " + tempo_format[idt])
            arquivo_saida = video_frames_dir / f"{tempo_format[idt]}_{frase}.png"
            comando = [str(FFMPEG_PATH), "-ss", tempo, "-i", str(video_name), "-frames:v", "1", str(arquivo_saida)]
            rodar_comando(comando)
    return video_frames_dir
