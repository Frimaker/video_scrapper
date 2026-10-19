from pathlib import Path
import yt_dlp
from config import FFMPEG_PATH, VIDEOS_DIR, nome_seguro


def download_video(url: str):
    # Configurações básicas
    VIDEOS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"URL: {url}")
    print(f"Diretório de Saída: {VIDEOS_DIR}")

    # Primeiro obtém as informações do vídeo
    with yt_dlp.YoutubeDL({
        'quiet': True,
        'no_warnings': True,
    }) as ydl:
        info = ydl.extract_info(url, download=False)

    titulo_original = info['title']
    video_id = info['id']

    # Cria um nome seguro para o arquivo
    titulo_seguro = nome_seguro(titulo_original)

    # Nome final do vídeo
    nome_arquivo = f"{titulo_seguro}_{video_id}.mp4"
    caminho_video = VIDEOS_DIR / nome_arquivo

    print(f"Título: {titulo_original}")
    print(f"Arquivo: {caminho_video}")

    # Configurações do download
    ydl_opts = {
        'outtmpl': str(VIDEOS_DIR / f"{titulo_seguro}_{video_id}.%(ext)s"),
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'ffmpeg_location': str(FFMPEG_PATH),
        'noprogress': False,
    }

    # Faz o download
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # Verifica se o arquivo foi realmente criado
    if not caminho_video.exists():
        raise FileNotFoundError(
            f"Vídeo não encontrado após o download: {caminho_video}"
        )

    print(f"Vídeo: {caminho_video}")

    return caminho_video