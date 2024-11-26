# Base image
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Install Python
RUN apt-get update && apt-get install -y \
    python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Set environment variables
ENV HF_HOME=/models

# Create models folder in the working directory
RUN mkdir -p $HF_HOME

# Install required Python packages and download the model
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt && \
python3 -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='diffusers/stable-diffusion-xl-1.0-inpainting-0.1', cache_dir='$HF_HOME')"    

# Copy the application code to the container
COPY . /app

# Set the entry point
# streamlit run --server.enableCORS=false --server.enableXsrfProtection=false --server.enableWebsocketCompression=false streamlit_app.py
ENTRYPOINT ["streamlit", "run", "--server.enableCORS=false", "--server.enableXsrfProtection=false", "--server.enableWebsocketCompression=false", "app.py"]
