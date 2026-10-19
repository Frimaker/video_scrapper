from pathlib import Path
import subprocess
from config import FFMPEG_PATH
import json
from dotenv import load_dotenv

def verificar_ffmpeg():
# Verifica se o executável do FFmpeg existe dentro do projeto
    if not FFMPEG_PATH.exists():
        raise RuntimeError(
            "FFmpeg não encontrado.\n"
            f"Esperado em: {FFMPEG_PATH}\n\n"
            "Certifique-se de que o arquivo ffmpeg.exe "
            "está dentro da pasta bin do projeto."
        )


def rodar_comando(comando):
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


def get_frames(video_name: Path, local_transcricao: Path):
    # Diretório onde este arquivo Python está localizado
    BASE_DIR = Path(__file__).resolve().parent
    load_dotenv(BASE_DIR / ".env")
    # Caminho do FFmpeg que está dentro do projeto
    FFMPEG_PATH = BASE_DIR / "bin" / "ffmpeg.exe"
    FRAMES_DIR = BASE_DIR / "video_frames"
    # cria antes o diretório onde os frames dos videos estarão
    FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    
    #video_read = Path("C:/AI/video_scrapper/videos/The_Dean's_List_-_Dear_Professor_(with_Lyrics)_NnyxkbnajgQ.mp4")
    # cria diretório para a pasta dos frames video 
    VIDEO_FRAMES_DIR = FRAMES_DIR / f"{video_name.stem}"
    # print("DIRETÓRIO DOS FRAMES DO VIDEO: " + str(VIDEO_FRAME_DIR))
    VIDEO_FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    
    # LEITURA read json file
    with open(local_transcricao, "r") as file:
        queries = json.load(file)
    # print(queries)

    for idq, q in enumerate(queries):
        # busca as queries
        query = queries[idq]["segmentos"]
        frase = queries[idq]["frase"]
        # lista limpa sempre que termina de ler uma query
        tempo_format =  []
        
        for idt, t in enumerate(query):
            print(idt, t)
            # busca o timestamp
            tempo = query[idt]["Tempo"]
            print("timestamps: " + query[idt]["Tempo"])

            # windows impede ":" para nomes, formato apenas para nomear os frames
            # str é estatico, replace funciona em str preexistente e não incoming variables
            # preencher a lista
            tempo_format.append(tempo)
            tempo_format[idt] = tempo_format[idt].replace(":", ".")
            print("FORMAT: " + tempo_format[idt])

            arquivo_saida = VIDEO_FRAMES_DIR / f"{tempo_format[idt]}_{frase}.png"

            #quando conectar o fluxo colcoar o nome do video no print para ser extraido pelo pytesseract
            #AGORA, fazer essa merda loopar e catar TODOS os segmentos relevantes e extrair frames

            comando = [
                str(FFMPEG_PATH),
                "-ss", tempo,
                "-i", str(video_name),
                "-frames:v", "1",
                str(arquivo_saida)
            ]
            #print("AAAAAA: " + str(comando))
            rodar_comando(comando)

    return VIDEO_FRAMES_DIR

# j = Path(r"C:\AI\video_scrapper\videos\Beverly_Be_The_One_(English_Ver.).mp4")
# caminho = Path(f"C:/AI/video_scrapper/relevancia/rankeamento_Beverly_Be_The_One_(English_Ver.).json")
# get_frames(j, caminho) 








    