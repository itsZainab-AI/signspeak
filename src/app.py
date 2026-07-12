import os
import tempfile

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from fastapi import Body

from src.knowledge_base import answer_question
from src.ocr_reader import extract_text
from src.translator import translate_and_explain

load_dotenv()

app = FastAPI(title="SignSpeak API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/scan")
async def scan_image(
    file: UploadFile = File(...),
    target_language: str = Form("en"),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    valid_extensions = (".png", ".jpg", ".jpeg", ".bmp", ".gif")
    if not file.filename or not file.filename.lower().endswith(valid_extensions):
        raise HTTPException(status_code=400, detail="File must have a valid image extension")

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".tmp")
    temp_path = temp_file.name
    temp_file.close()

    try:
        with open(temp_path, "wb") as destination:
            destination.write(await file.read())

        original_text = extract_text(temp_path)
        result = translate_and_explain(original_text, target_language)

        return {
            "original_text": original_text,
            "translation": result["translation"],
            "explanation": result["explanation"],
        }
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.post("/ask")
async def ask(question: str = Body(..., embed=True)):
    if not question or not question.strip():
        raise HTTPException(status_code=400, detail="Question must not be empty")

    answer = answer_question(question)
    return {"answer": answer}


@app.get("/health")
async def health():
    return {"status": "ok"}
