from pathlib import Path
import subprocess
from config import FFMPEG_PATH

# Diretório onde este arquivo Python está localizado

BASE_DIR = Path(__file__).resolve().parent

# Caminho do FFmpeg que está dentro do projeto

FFMPEG_PATH = BASE_DIR / "bin" / "ffmpeg.exe"

def verificar_ffmpeg():
# Verifica se o executável do FFmpeg existe dentro do projeto
    if not FFMPEG_PATH.exists():
        raise RuntimeError(
            "FFmpeg não encontrado.\n"
            f"Esperado em: {FFMPEG_PATH}\n\n"
            "Certifique-se de que o arquivo ffmpeg.exe "
            "está dentro da pasta bin do projeto."
        )

if not FFMPEG_PATH.is_file():
    raise RuntimeError(
        f"O caminho do FFmpeg não é um arquivo válido: {FFMPEG_PATH}"
    )

def extrair_audio(video: Path):
# Extrai o áudio do vídeo utilizando o FFmpeg
    if not video.exists():
        raise FileNotFoundError(
            f"Vídeo não encontrado: {video}"
        )

    if not video.is_file():
        raise FileNotFoundError(
            f"O caminho informado não é um arquivo: {video}"
        )

    # Verifica se o FFmpeg está disponível
    verificar_ffmpeg()

    # Cria o diretório de saída
    saida = BASE_DIR / "audios" / video.stem
    saida.parent.mkdir(parents=True, exist_ok=True)

    print(f"Vídeo: {video}")
    print(f"Saída: {saida}")
    print(f"Diretório de saída: {saida.parent}")

    # "audios/meu_video" + ".mp3"
    arquivo_saida = saida.with_suffix(".mp3")

    print(f"Arquivo de saída: {arquivo_saida}")

    # Comando do FFmpeg para extrair o áudio do vídeo
    #
    # -i  -> arquivo de entrada
    # -vn -> não utilizar o fluxo de vídeo
    # -y  -> sobrescrever o arquivo caso já exista
    comando = [
        str(FFMPEG_PATH),
        "-i",
        str(video),
        "-vn",
        "-y",
        str(arquivo_saida)
    ]

    print(f"Vídeo: {video}")
    print(f"Saída: {arquivo_saida}")
    print("Extraindo áudio...")

    resultado = subprocess.run(
        comando,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if resultado.returncode != 0:
        raise RuntimeError(
            "Erro durante a execução do FFmpeg:\n"
            f"{resultado.stderr}"
        )

    print("Áudio extraído com sucesso!")

    return arquivo_saida