FROM python:3.11-slim

# Tesseract OCR is a system package, needed for src/ocr_reader.py
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Render sets $PORT at runtime; default to 8000 for local Docker testing
ENV PORT=8000
EXPOSE 8000

CMD uvicorn src.app:app --host 0.0.0.0 --port $PORT
