import os
import json
import whisper

from pathlib import Path

from config import (
        FFMPEG_PATH,
        TRANSCRICOES_DIR,
        nome_seguro
    )


# Coloca o diretório do FFmpeg no PATH
os.environ["PATH"] = (
    str(FFMPEG_PATH.parent)
    + os.pathsep
    + os.environ.get("PATH", "")
)

def formatar_timestamp(segundos: float) -> str:
    """Converte segundos para HH:MM:SS.mmm."""
    horas = int(segundos // 3600)
    minutos = int((segundos % 3600) // 60)
    segs = int(segundos % 60)
    milissegundos = int(round((segundos - int(segundos)) * 1000))

    # Corrige o caso raro de arredondamento para 1000 ms.
    if milissegundos == 1000:
        segs += 1
        milissegundos = 0
        if segs == 60:
            minutos += 1
            segs = 0
        if minutos == 60:
            horas += 1
            minutos = 0

    return f"{horas:02d}:{minutos:02d}:{segs:02d}"


def whisper_transcribe(model_option: str, audio_input: Path):
    model = whisper.load_model(model_option)

    # word_timestamps=False é suficiente para timestamp por trecho.
    # Cada segmento retornado pelo Whisper possui início, fim e texto.
    result = model.transcribe(str(audio_input))

    TRANSCRICOES_DIR.mkdir(parents=True, exist_ok=True)

    nome = nome_seguro(audio_input.stem)

    arquivo_saida = (
        TRANSCRICOES_DIR
        / f"{model_option}_transcricao_{nome}.json"
    )

    transcricao_json = {
        "arquivo_audio": str(audio_input),
        "modelo": model_option,
        "idioma": result.get("language"),
        "segmentos": [
            {
                "inicio": formatar_timestamp(segmento["start"]),
                "fim": formatar_timestamp(segmento["end"]),
                "inicio_segundos": round(segmento["start"], 3),
                "fim_segundos": round(segmento["end"], 3),
                "texto": segmento["text"].strip(),
            }
            for segmento in result.get("segments", [])
        ],
    }

    with open(arquivo_saida, "w", encoding="utf-8") as f:
        json.dump(
            transcricao_json,
            f,
            ensure_ascii=False,
            indent=2
        )

    # Também retorna o JSON para quem chamar a função.
    print(json.dumps(transcricao_json, ensure_ascii=False, indent=2))
    print(f"Transcrição JSON salva em: {arquivo_saida}")

    return arquivo_saida
