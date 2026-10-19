from huggingface_hub import snapshot_download

model_id = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
destination =  r"C:/AI/video_scrapper/models/"

path = snapshot_download(
    repo_id=model_id,
    local_dir=destination
)

print(f"modelo baixado com sucesso: {path}")