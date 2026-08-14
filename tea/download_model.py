import os
from pathlib import Path

print("Downloading FastEmbed model (BAAI/bge-small-en-v1.5) for Render...")
try:
    from fastembed import TextEmbedding
    
    # Save cache inside the project directory so Render doesn't delete it after the build phase
    cache_path = str(Path(__file__).resolve().parent / "fastembed_cache")
    
    # This automatically downloads the ONNX model files to the local cache if missing
    embedding = TextEmbedding(model_name="BAAI/bge-small-en-v1.5", cache_dir=cache_path)
    print("Model downloaded successfully!")
except Exception as e:
    print(f"Error downloading model: {e}")
