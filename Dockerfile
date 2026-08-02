FROM python:3.10-slim

# 1. Install system dependencies required for PyAudio and Whisper
RUN apt-get update && apt-get install -y \
    gcc \
    portaudio19-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. Set up the user environment
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# 3. Set the main working directory for the app
WORKDIR $HOME/app

# 4. Copy requirements file and install Python packages
COPY --chown=user:user requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of your code (this copies your backend and frontend folders)
COPY --chown=user:user . .

EXPOSE 7860

# 6. Step INSIDE the backend folder to find main.py
WORKDIR $HOME/app/backend

# 7. Launch the FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
