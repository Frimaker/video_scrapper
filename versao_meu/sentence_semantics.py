from sentence_transformers import SentenceTransformer, util
import json
from pathlib import Path
from whisper_transcription import whisper_transcribe
from semantic_config import frases
from semantic_config import limite

# PATH = BASEDIR / modelo TROCAR

def rank_semantics(local_transcricao: Path, video_name: Path):
    # Carrega o modelo pré-treinado
    model = SentenceTransformer(
        # sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
        r"C:/AI/video_scrapper/models/paraphrase-multilingual-MiniLM-L12-v2",
        local_files_only=True
    )

    # LEITURA read json file
    with open(str(local_transcricao), "r") as file:
        data = json.load(file)
    # print(data)

    segments = data["segmentos"]

    # Exemplo de segmentos obtidos do Whisper
    # segments = [
    #     {
    #         "start": 195,
    #         "end": 210,
    #         "text": "Vamos investigar a falha de conexão com o banco."
    #     },
    #     {
    #         "start": 760,
    #         "end": 775,
    #         "text": "O servidor não consegue se comunicar com a base de dados."
    #     },
    #     {
    #         "start": 1510,
    #         "end": 1525,
    #         "text": "Vamos alterar a cor do botão da interface."
    #     }
    # ]

    # Gera os embeddings dos textos
    texts = [segment["texto"] for segment in segments]
    embeddings = model.encode(
        texts,
        convert_to_tensor=True,
        normalize_embeddings=True
    )

    # Pesquisa por significado, não por palavras exatas
    # query = ["I feel so hopeless"]
    # query = "I feel so hopeless"
    query = frases

    # Contém o resultado do rankeamento das frases de todas as queries
    semantic_ranked_queries = []

    for idq, q in enumerate(query):
        query_embedding = model.encode(
            query[idq],
            convert_to_tensor=True,
            normalize_embeddings=True
        )

        # Calcula a similaridade entre a consulta e os segmentos
        scores = util.cos_sim(query_embedding, embeddings)[0]

        # Ordena do mais relevante para o menos relevante
        #pytorch.argsort retorna um sequencia de indices que equivalem a posição dos tensors
        #em ordem descendente faz a lista de indices enfileirar seus numeros do + -> - score 
        ranking = scores.argsort(descending=True)

        # limite de respostas relevantes
        ranking = ranking[:limite]

        #faz loop neste array e joga pra json
        current_semantic_ranking = []

        #de-nesting tensors (a list with 1 element from a list of tensors) as a number
        for idx in ranking:
            i = idx.item()

            current_semantic_ranking.append(
                {
                    "Relevancia": round(scores[i].item(), 3),
                    "Tempo": f"{segments[i]['inicio']}",
                    "Texto": f"{segments[i]['texto']}"
                }
            )
        # print(
        #     f"Relevância: {scores[i].item():.3f} | "
        #     f"Tempo: {segments[i]['inicio']}s | "
        #     f"Texto: {segments[i]['texto']}"
        # )

        semantic_ranked_queries.append(
            {
                "frase": q,
                "segmentos": current_semantic_ranking
            }
        )

    caminho = Path(f"C:/AI/video_scrapper/relevancia/rankeamento_{video_name.stem}.json")

    with open(caminho, "w") as f:
        json.dump(
            semantic_ranked_queries,
            f,
            ensure_ascii=False,
            indent=2
        )

    return caminho

# t = Path("C:/AI/video_scrapper/transcricoes/large_transcricao_The_Dean's_List_-_Dear_Professor_(with_Lyrics)_NnyxkbnajgQ.json")
# j = Path(r"C:\AI\video_scrapper\videos\Beverly_Be_The_One_(English_Ver.).mp4")
# rank_semantics(t, j)
