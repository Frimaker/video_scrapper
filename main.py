import argparse
import sys

from whisper_transcription import whisper_transcribe
from ffmpeg_audio import verificar_ffmpeg, extrair_audio
from youtube_download import download_video


# O main:
# 1. organiza e ativa essas funções em ordem;
# 2. repassar os argumento de parse para elas;
# 3. ao fim, pode reportar um erro em caso de falha.
def main():
    parser = argparse.ArgumentParser(
        description="Extrai o ádio de um vídeo utilizando FFmpeg."
    )

    parser.add_argument(
        "url",
        help="URL do vídeo do YouTube"
    )

    parser.add_argument(
        "-m",
        "--model",
        default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Modelo do Whisper. Padrão: base"
    )

    args = parser.parse_args()

    try:
        verificar_ffmpeg()

        # retorna videos/meu_video.mp4
        video = download_video(
            url=args.url
        )

        arquivo_saida = extrair_audio(
            video=video
        )

        transcricao = whisper_transcribe(
            model_option=args.model,
            audio_input=arquivo_saida
        )

        return transcricao

    except Exception as erro:
        print(f"\nErro: {erro}", file=sys.stderr)
        sys.exit(1)


# Se este arquivo py está sendo chamado diretamente,
# chama a função main()
if __name__ == "__main__":
    main()