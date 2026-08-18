FROM python:3.11-slim-bullseye

WORKDIR /MoneyPrinterTurbo

ENV PYTHONPATH="/MoneyPrinterTurbo" \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN chmod 777 /MoneyPrinterTurbo

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    imagemagick \
    ffmpeg \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Fix ImageMagick security policy for MoviePy
RUN sed -i '/<policy domain="path" rights="none" pattern="@\*"/d' \
    /etc/ImageMagick-6/policy.xml

# Copy requirements first for Docker layer caching
COPY requirements.txt ./

RUN pip install --upgrade pip setuptools wheel

# ---------------------------------------------------------
# CPU-ONLY PYTORCH
# ---------------------------------------------------------
# Do NOT install CUDA/NVIDIA version.
RUN pip install \
    --index-url https://download.pytorch.org/whl/cpu \
    torch==2.6.0 \
    torchaudio==2.6.0

# ---------------------------------------------------------
# MoneyPrinter base dependencies
# ---------------------------------------------------------
RUN pip install --no-cache-dir -r requirements.txt

# ---------------------------------------------------------
# Chatterbox dependencies
#
# These versions follow the environment used by this fork.
# transformers 4.53.2 is intentionally used because WhisperX
# requires >=4.48 while the fork environment used 4.53.2.
# ---------------------------------------------------------
RUN pip install --no-cache-dir \
    numpy==2.2.6 \
    librosa==0.11.0 \
    s3tokenizer==0.2.0 \
    diffusers==0.29.0 \
    resemble-perth==1.0.1 \
    conformer==0.3.2 \
    safetensors==0.5.3 \
    transformers==4.53.2

# Chatterbox itself.
# --no-deps avoids replacing our CPU-only PyTorch installation.
RUN pip install --no-cache-dir --no-deps \
    chatterbox-tts==0.1.2

# ---------------------------------------------------------
# WhisperX dependencies
# ---------------------------------------------------------
RUN pip install --no-cache-dir \
    "ctranslate2<4.5.0" \
    "faster-whisper>=1.1.1" \
    "nltk>=3.9.1" \
    "numpy>=2.0.2" \
    "onnxruntime>=1.19" \
    "pandas>=2.2.3" \
    "pyannote-audio>=3.3.2"

# Install WhisperX without letting pip replace torch/torchaudio.
RUN pip install --no-cache-dir --no-deps \
    whisperx==3.4.2

# Application
COPY . .

RUN chmod -R a+rwX /MoneyPrinterTurbo

EXPOSE 8501 8080

CMD ["streamlit", "run", "./webui/Main.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true", "--browser.gatherUsageStats=false"]