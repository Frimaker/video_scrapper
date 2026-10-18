"""
Transcrição visual de imagens usando OCR.

Objetivo:
- ler todas as imagens de uma pasta;
- executar OCR em cada imagem;
- guardar o texto encontrado e os blocos reconhecidos;
- gerar um JSON consolidado.

Dependências Python:
    py -m pip install pillow pytesseract python-dotenv

Além disso, o Tesseract OCR precisa estar instalado na máquina.
Este arquivo aceita:
    1. Tesseract disponível no PATH;
    2. Tesseract dentro de bin/tesseract.exe do projeto; ou
    3. caminho informado pela variável TESSERACT_CMD no .env.

Exemplo:
    py visual_transcription.py "frames"

Definir o arquivo JSON de saída:
    py visual_transcription.py "frames" --output "resultado.json"

Usar somente português:
    py visual_transcription.py "frames" --lang por
"""

import argparse
import json
import os
import shutil
from pathlib import Path

import pytesseract
from PIL import Image, UnidentifiedImageError
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

VISUAIS_DIR = BASE_DIR / "transcricoes_visuais"

EXTENSOES_IMAGEM = {
    ".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp"
}


def obter_tesseract() -> str:
    """Localiza o executável do Tesseract."""

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

    encontrado = shutil.which("tesseract")
    if encontrado:
        return encontrado

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


def executar_ocr(imagem: Image.Image, idioma: str) -> tuple[str, list]:
    """Executa OCR e retorna o texto consolidado e os blocos reconhecidos."""

    dados = pytesseract.image_to_data(
        imagem,
        lang=idioma,
        output_type=pytesseract.Output.DICT,
        config="--psm 6",
    )

    textos = []
    blocos = []

    for i, texto_bruto in enumerate(dados["text"]):
        texto = texto_bruto.strip()
        if not texto:
            continue

        try:
            confianca = float(dados["conf"][i])
        except (ValueError, TypeError):
            confianca = -1.0

        if confianca < 0:
            continue

        x = int(dados["left"][i])
        y = int(dados["top"][i])
        largura = int(dados["width"][i])
        altura = int(dados["height"][i])

        textos.append(texto)
        blocos.append({
            "texto": texto,
            "confianca": round(confianca, 2),
            "caixa": {
                "x": x,
                "y": y,
                "largura": largura,
                "altura": altura,
            },
        })

    return " ".join(textos), blocos


def processar_pasta(
    pasta: Path,
    arquivo_saida: Path | None = None,
    idioma_ocr: str = "por+eng",
) -> dict:
    """Processa todas as imagens compatíveis encontradas diretamente na pasta."""

    if not pasta.exists():
        raise FileNotFoundError(f"Pasta não encontrada: {pasta}")
    if not pasta.is_dir():
        raise NotADirectoryError(f"O caminho informado não é uma pasta: {pasta}")

    tesseract = obter_tesseract()
    pytesseract.pytesseract.tesseract_cmd = tesseract

    imagens = sorted(
        (
            caminho for caminho in pasta.iterdir()
            if caminho.is_file() and caminho.suffix.lower() in EXTENSOES_IMAGEM
        ),
        key=lambda caminho: caminho.name.lower(),
    )

    if not imagens:
        raise FileNotFoundError(
            f"Nenhuma imagem compatível foi encontrada na pasta: {pasta}"
        )

    if arquivo_saida is None:
        VISUAIS_DIR.mkdir(parents=True, exist_ok=True)
        arquivo_saida = VISUAIS_DIR / f"{pasta.name}_visual.json"
    else:
        arquivo_saida.parent.mkdir(parents=True, exist_ok=True)

    resultado = {
        "pasta_origem": str(pasta.resolve()),
        "ocr": {
            "motor": "Tesseract OCR",
            "idioma": idioma_ocr,
            "configuracao": "--psm 6",
        },
        "resumo": {
            "imagens_encontradas": len(imagens),
            "imagens_processadas": 0,
            "imagens_com_texto": 0,
            "imagens_com_erro": 0,
        },
        "imagens": [],
    }

    print(f"Pasta: {pasta.resolve()}")
    print(f"Imagens encontradas: {len(imagens)}")
    print(f"Tesseract: {tesseract}")
    print("Processando imagens...")

    for indice, caminho in enumerate(imagens, start=1):
        registro = {
            "arquivo": caminho.name,
            "caminho": str(caminho.resolve()),
        }

        try:
            with Image.open(caminho) as imagem_original:
                imagem = imagem_original.convert("RGB")
                largura, altura = imagem.size
                texto, blocos = executar_ocr(imagem, idioma_ocr)

            registro.update({
                "largura": largura,
                "altura": altura,
                "texto": texto,
                "blocos": blocos,
                "erro": None,
            })

            resultado["resumo"]["imagens_processadas"] += 1
            if texto:
                resultado["resumo"]["imagens_com_texto"] += 1
                print(f"[{indice}/{len(imagens)}] {caminho.name}: {texto}")
            else:
                print(f"[{indice}/{len(imagens)}] {caminho.name}: (nenhum texto detectado)")

        except (UnidentifiedImageError, OSError, pytesseract.TesseractError) as erro:
            registro.update({
                "texto": "",
                "blocos": [],
                "erro": str(erro),
            })
            resultado["resumo"]["imagens_com_erro"] += 1
            print(f"[{indice}/{len(imagens)}] Erro em {caminho.name}: {erro}")

        resultado["imagens"].append(registro)

    with arquivo_saida.open("w", encoding="utf-8") as arquivo:
        json.dump(resultado, arquivo, ensure_ascii=False, indent=2)

    print("\nProcessamento concluído.")
    print(f"JSON salvo em: {arquivo_saida.resolve()}")

    return resultado


def main():
    parser = argparse.ArgumentParser(
        description="Lê imagens de uma pasta usando OCR e salva o resultado em JSON."
    )
    parser.add_argument(
        "pasta",
        help="Caminho para a pasta que contém as imagens.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Caminho opcional do JSON de saída. Padrão: transcricoes_visuais/<nome_da_pasta>_visual.json",
    )
    parser.add_argument(
        "--lang",
        default="por+eng",
        help="Idiomas do Tesseract. Padrão: por+eng",
    )

    args = parser.parse_args()

    try:
        processar_pasta(
            pasta=Path(args.pasta),
            arquivo_saida=args.output,
            idioma_ocr=args.lang,
        )
    except Exception as erro:
        print(f"\nErro: {erro}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
