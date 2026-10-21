# video_scrapper

Projeto Python que baixa um vídeo do YouTube e executa o pipeline existente de extração de áudio, transcrição com Whisper, ranqueamento semântico, extração de frames e OCR. Esta refatoração organiza os caminhos e responsabilidades em módulos; a sequência funcional do `main.py` foi mantida.

## 1. Requisitos externos

- Python 3.10 ou versão compatível com as dependências instaladas.
- FFmpeg instalado no sistema **ou** executável local em `bin/ffmpeg.exe`.
- Tesseract OCR instalado no sistema ou disponibilizado no projeto.
- Conexão com a internet para baixar vídeos, instalar pacotes e baixar o modelo do Hugging Face.

FFmpeg e Tesseract são programas externos: `pip install -r requirements.txt` instala pacotes Python, mas não instala esses executáveis.

## 2. Preparar a configuração

1. Na raiz do projeto, copie `.env.example` para `.env`.
2. Edite `.env`:
   - `FFMPEG_MODE=LOCAL` usa `FFMPEG_LOCAL_PATH` relativo à raiz do projeto (padrão `bin/ffmpeg.exe`).
   - `FFMPEG_MODE=PATH` procura `ffmpeg` no `PATH` do sistema.
   - `TESSERACT_CMD` pode apontar para o executável do Tesseract. O caminho relativo é resolvido a partir da raiz do projeto.
3. Coloque os executáveis nos caminhos configurados ou instale-os no sistema e ajuste o `.env`.

O arquivo `.env` é local e não deve ser enviado ao repositório. O arquivo `.env.example` serve como modelo.

## 3. Criar e ativar o ambiente virtual (Windows)

Abra o PowerShell na pasta do projeto e execute:

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
```

Se o PowerShell bloquear scripts por política de execução, use o Prompt de Comando (cmd):

```bat
py -m venv venv
venv\Scripts\activate.bat
```

Quando ativado, o terminal normalmente mostra `(venv)` no início da linha. Para sair do ambiente virtual, execute `deactivate`.

## 4. Instalar dependências e baixar o modelo

Com o ambiente virtual ativado, escolha uma das opções:

**Opção recomendada — um único comando no Windows:**

```bat
install.bat
```

O script instala `requirements.txt` e, em seguida, executa `hugger.py` para baixar o modelo `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` para a pasta `models/`.

**Ou executar as etapas manualmente:**

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python hugger.py
```

O `pip` não oferece um mecanismo padrão e confiável para executar `hugger.py` automaticamente ao instalar um `requirements.txt`. Por isso, o download do modelo foi colocado no `install.bat` como etapa explícita, além de continuar disponível manualmente. O download requer internet e pode levar algum tempo.

## 5. Executar o projeto

Na raiz do projeto, com `venv` ativado e as dependências/modelo instalados:

```powershell
python main.py "https://www.youtube.com/watch?v=ID_DO_VIDEO"
```

O argumento obrigatório é a URL do vídeo. Para selecionar o modelo do Whisper, use `-m` ou `--model`:

```powershell
python main.py "https://www.youtube.com/watch?v=ID_DO_VIDEO" --model base
```

Modelos aceitos: `tiny`, `base`, `small`, `medium` e `large`. O padrão é `base`. Modelos maiores tendem a consumir mais memória e demorar mais para processar.

Também é possível usar um link do formato YouTube Shorts:

```powershell
python main.py "https://youtube.com/shorts/ID_DO_VIDEO" --model small
```

## 6. Etapas executadas pelo `main.py`

1. Verifica a disponibilidade do FFmpeg.
2. Baixa o vídeo do YouTube.
3. Extrai o áudio em MP3.
4. Transcreve o áudio com Whisper e salva JSON com timestamps.
5. Compara os segmentos transcritos com as frases de `semantic_config.py`.
6. Extrai frames dos timestamps selecionados pelo ranqueamento.
7. Executa OCR nos frames e salva o JSON visual.

As frases e o limite de resultados semânticos ficam em `semantic_config.py`. Esta configuração não altera o modelo de transcrição do Whisper.

## 7. Estrutura dos módulos

- `main.py`: coordena o pipeline, argumentos de linha de comando e tratamento de erros.
- `config.py`: raiz do projeto, caminhos de entrada/saída, FFmpeg, Tesseract e modelo semântico.
- `youtube_download.py`: download do vídeo.
- `ffmpeg_audio.py`: extração de áudio.
- `whisper_transcription.py`: transcrição de áudio e JSON com timestamps.
- `semantic_config.py`: frases consultadas e quantidade de resultados do ranqueamento.
- `sentence_semantics.py`: ranqueamento semântico dos segmentos.
- `ffmpeg_frame.py`: extração de frames nos timestamps ranqueados.
- `visual_transcription.py`: OCR e gravação do resultado visual.
- `hugger.py`: download local do modelo semântico.
- `requirements.txt`: dependências Python.
- `install.bat`: instalação das dependências seguida do download do modelo.

## 8. Pastas geradas

O programa cria as pastas necessárias durante a execução:

- `videos/`: vídeos baixados.
- `audios/`: áudio extraído.
- `transcricoes/`: transcrição do Whisper.
- `rankeamento/`: segmentos selecionados semanticamente.
- `video_frames/`: imagens extraídas.
- `transcricoes_visuais/`: resultados de OCR.
- `models/`: modelo semântico baixado pelo `hugger.py`.

Essas pastas e o ambiente virtual são locais e estão no `.gitignore`.

## 9. Solução de problemas

- **FFmpeg não encontrado:** confira `FFMPEG_MODE` e `FFMPEG_LOCAL_PATH` no `.env`, ou configure o FFmpeg no `PATH` e use `FFMPEG_MODE=PATH`.
- **Tesseract não encontrado:** confira `TESSERACT_CMD` e se o arquivo existe; alternativamente, instale Tesseract e disponibilize `tesseract` no `PATH`.
- **Modelo semântico ausente:** ative o `venv` e execute `python hugger.py` novamente.
- **Comando `python` não encontrado:** verifique a instalação do Python e tente `py` no Windows.
- **Falha ao baixar vídeo/modelo:** verifique a conexão de internet e tente novamente.
