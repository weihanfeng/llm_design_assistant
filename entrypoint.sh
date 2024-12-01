#!/bin/bash

# Check if the MODEL environment variable is set
if [ -z "$MODEL" ]; then
  echo "Error: MODEL environment variable is not set. Please set it to the Hugging Face repo ID."
  exit 1
fi

# Download the model
echo "Downloading the model from repo: $MODEL..."
python3 -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='$MODEL')"

# Start the Streamlit server
echo "Starting the Streamlit server..."
exec streamlit run --server.enableCORS=false --server.enableXsrfProtection=false --server.enableWebsocketCompression=false src/app.py
