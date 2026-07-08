from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import os

load_dotenv()

from src.ocr_reader import extract_text_from_image
from src.translator import translate_text
from src.knowledge_base import lookup_sign, get_all_signs

app = FastAPI(title="SignSpeak API")

app.mount("/static", StaticFiles(directory="static"), name="static")

TRANSLATION_API_KEY = os.getenv("TRANSLATION_API_KEY")
if not TRANSLATION_API_KEY:
    print("Warning: TRANSLATION_API_KEY not set in .env")


@app.get("/")
def read_root():
    return FileResponse("static/index.html")


@app.get("/api/signs")
def list_signs():
    return get_all_signs()


@app.post("/api/upload-image")
async def upload_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(await file.read())
    try:
        extracted_text = extract_text_from_image(temp_path)
        translated = translate_text(extracted_text)
        sign_meaning = lookup_sign(extracted_text)
        return {
            "filename": file.filename,
            "extracted_text": extracted_text,
            "translated_text": translated,
            "sign_meaning": sign_meaning,
        }
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.post("/api/translate")
def translate_endpoint(text: str, target_language: str = "en"):
    return {"original_text": text, "translated_text": translate_text(text, target_language)}


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
