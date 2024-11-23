# Base image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Set environment variables
ENV HF_HOME=/app/models

# Create models folder in the working directory
RUN mkdir -p $HF_HOME

# Install required Python packages and download the model
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt && \
python3 -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='diffusers/stable-diffusion-xl-1.0-inpainting-0.1', cache_dir='$HF_HOME')"    

# Copy the application code to the container
COPY . /app

# Set the entry point
ENTRYPOINT ["python3", "app.py"]
