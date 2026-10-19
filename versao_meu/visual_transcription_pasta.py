import json
import os
import shutil
from pathlib import Path

import pytesseract
from dotenv import load_dotenv
from PIL import Image

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

tesseract = obter_tesseract()
pytesseract.pytesseract.tesseract_cmd = tesseract



###################
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

    return " ".join(textos)

def transcribe_frames(diretorio: Path):
    # busca a quantidade e nomes de arquivos
    #diretorio = Path(r"C:\AI\video_scrapper\video_frames\The_Dean's_List_-_Dear_Professor_(with_Lyrics)_NnyxkbnajgQ")
    arquivos = [arquivo.name for arquivo in diretorio.iterdir()
                if arquivo.is_file()]
    quantidade = len(arquivos)

    transcricao = []
    tempo = []
    frase = []

    for i in range(quantidade):
        frame = diretorio / arquivos[i]
        #print(frame)
        texto = executar_ocr(str(frame))
        #print(texto)

        tempo.append(arquivos[i])
        tempo[i] = tempo[i].split("_")[0]
        frase.append(arquivos[i])
        frase[i] = frase[i].split("_")[1]
        transcricao.append(
            {
                "Frase": frase[i],
                "Tempo": tempo[i],
                "Texto": texto
            }
        )

    #print(json.dumps(transcricao, ensure_ascii=False, indent=2))

    arquivo_saida = VISUAIS_DIR / f"{diretorio.stem}.json"

    with open(arquivo_saida, "w") as f:
        json.dump(
            transcricao,
            f,
            ensure_ascii=False,
            indent=2
        )
    return

# diretorio = Path(r"C:\AI\video_scrapper\video_frames\Beverly_Be_The_One_(English_Ver.)")

# transcribe_frames(diretorio)

###################


# def transcrever_imagem(caminho_imagem):
#     imagem = Image.open(caminho_imagem)

#     texto = pytesseract.image_to_string(
#         imagem,
#         lang="por+eng"
#     )

#     return texto.strip()

# texto = transcrever_imagem(
#     "C:/AI/video_scrapper/video_frames/The_Dean's_List_-_Dear_Professor_(with_Lyrics)_NnyxkbnajgQ/00.00.31_I feel so hopeless.png"
# )

# print(texto)


