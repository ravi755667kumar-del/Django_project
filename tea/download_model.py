import os

print("Downloading FastEmbed model (BAAI/bge-small-en-v1.5) for Render...")
try:
    from fastembed import TextEmbedding
    # This automatically downloads the ONNX model files to the local cache if missing
    embedding = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
    print("Model downloaded successfully!")
except Exception as e:
    print(f"Error downloading model: {e}")
