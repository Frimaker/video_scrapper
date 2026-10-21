import argparse
import sys

from whisper_transcription import whisper_transcribe
from ffmpeg_audio import verificar_ffmpeg, extrair_audio
from youtube_download import download_video
from sentence_semantics import rank_semantics
from ffmpeg_frame import get_frames
from visual_transcription import transcribe_frames


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

        local_transcricao = whisper_transcribe(
            model_option=args.model,
            audio_input=arquivo_saida
        )

        rankeamento = rank_semantics(
            local_transcricao=local_transcricao,
            video_name=video
        )

        video_frames = get_frames(
            video_name=video,
            local_transcricao=rankeamento
        )

        frame_transcription = transcribe_frames(
            diretorio=video_frames
        )

    except Exception as erro:
        print(f"\nErro: {erro}", file=sys.stderr)
        sys.exit(1)


# Se este arquivo py está sendo chamado diretamente,
# chama a função main()
if __name__ == "__main__":
    main()