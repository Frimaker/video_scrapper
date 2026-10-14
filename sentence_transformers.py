
from sentence_transformers import SentenceTransformer, util

# Carrega o modelo pré-treinado
model = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

# Exemplo de segmentos obtidos do Whisper
segments = [
    {
        "start": 195,
        "end": 210,
        "text": "Vamos investigar a falha de conexão com o banco."
    },
    {
        "start": 760,
        "end": 775,
        "text": "O servidor não consegue se comunicar com a base de dados."
    },
    {
        "start": 1510,
        "end": 1525,
        "text": "Vamos alterar a cor do botão da interface."
    }
]

# Gera os embeddings dos textos
texts = [segment["text"] for segment in segments]
embeddings = model.encode(
    texts,
    convert_to_tensor=True,
    normalize_embeddings=True
)

# Pesquisa por significado, não por palavras exatas
query = "Problemas de comunicação com o banco de dados"

query_embedding = model.encode(
    query,
    convert_to_tensor=True,
    normalize_embeddings=True
)

# Calcula a similaridade entre a consulta e os segmentos
scores = util.cos_sim(query_embedding, embeddings)[0]

# Ordena do mais relevante para o menos relevante
ranking = scores.argsort(descending=True)

for idx in ranking:
    i = idx.item()
    print(
        f"Relevância: {scores[i].item():.3f} | "
        f"Tempo: {segments[i]['start']}s | "
        f"Texto: {segments[i]['text']}"
    )
