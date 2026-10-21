from huggingface_hub import snapshot_download
from config import BASE_DIR

model_id = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
destination =  BASE_DIR / "models" / "paraphrase-multilingual-MiniLM-L12-v2"

path = snapshot_download(
    repo_id=model_id,
    local_dir=str(destination)
)

print(f"modelo baixado com sucesso: {path}")