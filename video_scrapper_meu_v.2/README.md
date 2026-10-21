# video_scrapper
Download videos to scrap audio and video text.
criar arquivo de nome ".env" e ter o seguinte conteudo:
# LOCAL = usa FFmpeg dentro do projeto
# PATH  = usa FFmpeg instalado na máquina
FFMPEG_MODE=LOCAL

# Usado somente quando FFMPEG_MODE=LOCAL
FFMPEG_LOCAL_PATH=bin/ffmpeg.exe
TESSERACT_CMD=bin/Tesseract-OCR/tesseract.exe

# https://www.youtube.com/watch?v=A3yCcXgbKrE
