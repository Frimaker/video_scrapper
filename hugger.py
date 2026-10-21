"""Baixa o modelo semântico utilizado pelo sentence_semantics.py."""

from huggingface_hub import snapshot_download
from config import SEMANTIC_MODEL_ID, SEMANTIC_MODEL_DIR


def baixar_modelo():
    SEMANTIC_MODEL_DIR.parent.mkdir(parents=True, exist_ok=True)
    path = snapshot_download(repo_id=SEMANTIC_MODEL_ID, local_dir=str(SEMANTIC_MODEL_DIR))
    print(f"Modelo baixado com sucesso: {path}")
    return path


if __name__ == "__main__":
    baixar_modelo()
