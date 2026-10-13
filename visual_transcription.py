"""
Transcrição visual de vídeo usando OCR.

Objetivo desta primeira etapa:
- abrir um vídeo;
- processar frames em intervalos definidos;
- executar OCR em cada frame;
- guardar o texto encontrado junto com o timestamp;
- gerar um JSON que poderá ser combinado posteriormente com a
  transcrição do áudio feita pelo Whisper.

IMPORTANTE:
OCR identifica principalmente TEXTO presente na imagem.
Ele não descreve, por si só, ações ou objetos da cena.
A descrição de "o que está acontecendo" será uma etapa posterior
de visão computacional/modelo multimodal.

Dependências Python:
    py -m pip install opencv-python pytesseract

Além disso, o Tesseract OCR precisa estar instalado na máquina.
Este arquivo aceita:
    1. Tesseract disponível no PATH; ou
    2. Tesseract dentro de bin/tesseract.exe do projeto; ou
    3. caminho informado pela variável TESSERACT_CMD no .env.

Exemplo:
    py visual_transcription.py "videos/meu_video.mp4"

Processar um frame por segundo:
    py visual_transcription.py "videos/meu_video.mp4" --interval 1

Processar dois frames por segundo:
    py visual_transcription.py "videos/meu_video.mp4" --interval 0.5
"""

import argparse
import json
import os
import shutil
from pathlib import Path

import cv2
import pytesseract
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

VISUAIS_DIR = BASE_DIR / "transcricoes_visuais"


def obter_tesseract() -> str:
    """
    Localiza o executável do Tesseract sem exigir alteração
    permanente nas variáveis de ambiente do Windows.
    """

    configurado = os.getenv("TESSERACT_CMD")

    if configurado:
        caminho = Path(configurado)

        if not caminho.is_absolute():
            caminho = BASE_DIR / caminho

        if caminho.is_file():
            return str(caminho)

        raise FileNotFoundError(
            f"TESSERACT_CMD foi configurado, mas o arquivo não existe: {caminho}"
        )

    # Procura no PATH
    encontrado = shutil.which("tesseract")

    if encontrado:
        return encontrado

    # Procura uma instalação local no projeto
    local = BASE_DIR / "bin" / "tesseract.exe"

    if local.is_file():
        return str(local)

    raise FileNotFoundError(
        "Tesseract OCR não encontrado.\n\n"
        "Opções:\n"
        "1. Instale o Tesseract e deixe-o disponível no PATH;\n"
        "2. coloque tesseract.exe em bin/;\n"
        "3. configure TESSERACT_CMD no arquivo .env."
    )


def formatar_timestamp(segundos: float) -> str:
    """Converte segundos para HH:MM:SS.mmm."""

    horas = int(segundos // 3600)
    minutos = int((segundos % 3600) // 60)
    segs = int(segundos % 60)
    milissegundos = int(round((segundos - int(segundos)) * 1000))

    if milissegundos == 1000:
        segs += 1
        milissegundos = 0

    if segs == 60:
        minutos += 1
        segs = 0

    if minutos == 60:
        horas += 1
        minutos = 0

    return f"{horas:02d}:{minutos:02d}:{segs:02d}.{milissegundos:03d}"


def executar_ocr(frame):
    """
    Executa OCR no frame.

    Retorna:
        texto: texto consolidado encontrado
        blocos: informações individuais dos textos encontrados
    """

    dados = pytesseract.image_to_data(
        frame,
        output_type=pytesseract.Output.DICT,
        config="--psm 6",
    )

    textos = []
    blocos = []

    quantidade = len(dados["text"])

    for i in range(quantidade):
        texto = dados["text"][i].strip()

        if not texto:
            continue

        try:
            confianca = float(dados["conf"][i])
        except (ValueError, TypeError):
            confianca = -1.0

        # Ignora resultados com confiança inválida.
        if confianca < 0:
            continue

        x = int(dados["left"][i])
        y = int(dados["top"][i])
        largura = int(dados["width"][i])
        altura = int(dados["height"][i])

        textos.append(texto)

        blocos.append(
            {
                "texto": texto,
                "confianca": round(confianca, 2),
                "caixa": {
                    "x": x,
                    "y": y,
                    "largura": largura,
                    "altura": altura,
                },
            }
        )

    return " ".join(textos), blocos


def processar_video(
    video: Path,
    intervalo: float = 1.0,
    idioma_ocr: str = "por+eng",
):
    """
    Processa o vídeo e gera um JSON com os textos encontrados
    nos frames e seus respectivos timestamps.

    intervalo:
        Quantidade de segundos entre os frames processados.
        Ex.: 1.0 = 1 frame por segundo.
        Ex.: 0.5 = 2 frames por segundo.
        Ex.: 2.0 = 1 frame a cada 2 segundos.
    """

    if not video.exists():
        raise FileNotFoundError(f"Vídeo não encontrado: {video}")

    if not video.is_file():
        raise FileNotFoundError(
            f"O caminho informado não é um arquivo: {video}"
        )

    if intervalo <= 0:
        raise ValueError("O intervalo precisa ser maior que zero.")

    tesseract = obter_tesseract()
    pytesseract.pytesseract.tesseract_cmd = tesseract

    # Define o idioma do OCR.
    # O usuário pode alterar pelo argumento --lang.
    idioma = idioma_ocr

    cap = cv2.VideoCapture(str(video))

    if not cap.isOpened():
        raise RuntimeError(
            f"Não foi possível abrir o vídeo: {video}"
        )

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    largura = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    altura = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    if fps <= 0:
        cap.release()
        raise RuntimeError("Não foi possível determinar o FPS do vídeo.")

    duracao = total_frames / fps if total_frames > 0 else 0

    VISUAIS_DIR.mkdir(parents=True, exist_ok=True)

    arquivo_saida = (
        VISUAIS_DIR
        / f"{video.stem}_visual.json"
    )

    resultado = {
        "arquivo_video": str(video),
        "arquivo_video_nome": video.name,
        "ocr": {
            "motor": "Tesseract OCR",
            "idioma": idioma,
            "intervalo_segundos": intervalo,
        },
        "video": {
            "fps": round(fps, 3),
            "total_frames": total_frames,
            "largura": largura,
            "altura": altura,
            "duracao_segundos": round(duracao, 3),
        },
        "frames": [],
    }

    print(f"Vídeo: {video}")
    print(f"FPS: {fps:.2f}")
    print(f"Duração: {duracao:.2f} segundos")
    print(f"Intervalo OCR: {intervalo} segundo(s)")
    print(f"Tesseract: {tesseract}")
    print("Processando frames...")

    # Controle por timestamp para evitar depender de leitura sequencial
    # exata quando o vídeo possui muitos frames.
    proximo_timestamp = 0.0
    frame_processado = 0

    while True:
        sucesso, frame = cap.read()

        if not sucesso:
            break

        timestamp = (
            cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
        )

        if timestamp + 0.001 < proximo_timestamp:
            continue

        texto, blocos = executar_ocr(frame)

        registro = {
            "frame": frame_processado,
            "timestamp": formatar_timestamp(timestamp),
            "timestamp_segundos": round(timestamp, 3),
            "texto": texto,
            "blocos": blocos,
        }

        resultado["frames"].append(registro)

        frame_processado += 1
        proximo_timestamp += intervalo

        if texto:
            print(
                f"[{formatar_timestamp(timestamp)}] "
                f"{texto}"
            )
        else:
            print(
                f"[{formatar_timestamp(timestamp)}] "
                "(nenhum texto detectado)"
            )

    cap.release()

    # Remove informações que podem não existir dependendo do vídeo.
    resultado["resumo"] = {
        "frames_processados": len(resultado["frames"]),
        "frames_com_texto": sum(
            1
            for frame in resultado["frames"]
            if frame["texto"]
        ),
    }

    with open(
        arquivo_saida,
        "w",
        encoding="utf-8",
    ) as arquivo:
        json.dump(
            resultado,
            arquivo,
            ensure_ascii=False,
            indent=2,
        )

    print("\nProcessamento concluído.")
    print(f"JSON salvo em: {arquivo_saida}")

    return resultado


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Extrai texto de frames de um vídeo usando OCR "
            "e salva o resultado em JSON."
        )
    )

    parser.add_argument(
        "video",
        help="Caminho para o arquivo de vídeo.",
    )

    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help=(
            "Intervalo entre frames processados em segundos. "
            "Padrão: 1.0"
        ),
    )

    parser.add_argument(
        "--lang",
        default="por+eng",
        help=(
            "Idiomas do Tesseract. "
            "Padrão: por+eng"
        ),
    )

    args = parser.parse_args()

    try:
        processar_video(
            video=Path(args.video),
            intervalo=args.interval,
            idioma_ocr=args.lang,
        )

    except Exception as erro:
        print(f"\nErro: {erro}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
