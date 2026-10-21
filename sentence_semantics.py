"""Ranqueamento semântico dos segmentos da transcrição do Whisper."""

import json
from pathlib import Path

from sentence_transformers import SentenceTransformer, util
from semantic_config import frases, limite
from config import SEMANTIC_MODEL_DIR, RANK_DIR


def rank_semantics(local_transcricao: Path, video_name: Path):
    RANK_DIR.mkdir(parents=True, exist_ok=True)
    model = SentenceTransformer(str(SEMANTIC_MODEL_DIR), local_files_only=True)

    with open(local_transcricao, "r", encoding="utf-8") as file:
        data = json.load(file)
    segments = data["segmentos"]
    texts = [segment["texto"] for segment in segments]
    embeddings = model.encode(texts, convert_to_tensor=True, normalize_embeddings=True)
    query = frases
    semantic_ranked_queries = []

    for idq, q in enumerate(query):
        query_embedding = model.encode(query[idq], convert_to_tensor=True, normalize_embeddings=True)
        scores = util.cos_sim(query_embedding, embeddings)[0]
        ranking = scores.argsort(descending=True)
        ranking = ranking[:limite]
        current_semantic_ranking = []
        for idx in ranking:
            i = idx.item()
            current_semantic_ranking.append({
                "Relevancia": round(scores[i].item(), 3),
                "Tempo": f"{segments[i]['inicio']}",
                "Texto": f"{segments[i]['texto']}"
            })
        semantic_ranked_queries.append({"frase": q, "segmentos": current_semantic_ranking})

    caminho = RANK_DIR / f"rankeamento_{video_name.stem}.json"
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(semantic_ranked_queries, f, ensure_ascii=False, indent=2)
    return caminho
