import os
import tempfile

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile, Body
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool
from starlette.requests import Request
from fastapi.staticfiles import StaticFiles
from src.knowledge_base import answer_question
from src.ocr_reader import OCRError, extract_text
from src.translator import TranslationError, translate_and_explain

load_dotenv()

MAX_UPLOAD_SIZE = 5 * 1024 * 1024
ALLOWED_IMAGE_CONTENT_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/bmp", "image/gif"}
ALLOWED_IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".bmp", ".gif")
MAX_QUESTION_LENGTH = 1000
MAX_LANGUAGE_LENGTH = 50

app = FastAPI(title="SignSpeak API")

def normalize_content_type(value: str | None) -> str | None:
    if not value:
        return None
    return value.split(";", 1)[0].strip().lower()


def validate_non_empty_string(value: str, name: str, max_length: int) -> str:
    if not isinstance(value, str):
        raise HTTPException(status_code=400, detail=f"{name} must be a string")
    stripped = value.strip()
    if not stripped:
        raise HTTPException(status_code=400, detail=f"{name} must not be empty")
    if len(stripped) > max_length:
        raise HTTPException(status_code=400, detail=f"{name} must be at most {max_length} characters")
    return stripped


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"detail": "Invalid request parameters"})


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

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
    content_type = normalize_content_type(file.content_type)
    if not content_type or content_type not in ALLOWED_IMAGE_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="File must be a supported image type")

    if not file.filename or not file.filename.lower().endswith(ALLOWED_IMAGE_EXTENSIONS):
        raise HTTPException(status_code=400, detail="File must have a valid image extension")

    target_language = validate_non_empty_string(target_language, "Target language", MAX_LANGUAGE_LENGTH)

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".tmp")
    temp_path = temp_file.name
    temp_file.close()

    try:
        file_bytes = await file.read(MAX_UPLOAD_SIZE + 1)
        if not file_bytes:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
        if len(file_bytes) > MAX_UPLOAD_SIZE:
            raise HTTPException(status_code=400, detail="Uploaded file exceeds the 5MB size limit")

        with open(temp_path, "wb") as destination:
            destination.write(file_bytes)

        try:
            original_text = await run_in_threadpool(extract_text, temp_path)
            result = await run_in_threadpool(translate_and_explain, original_text, target_language)
        except OCRError as e:
            raise HTTPException(status_code=422, detail=str(e))
        except TranslationError as e:
            raise HTTPException(status_code=502, detail=str(e))

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
    question = validate_non_empty_string(question, "Question", MAX_QUESTION_LENGTH)

    answer = answer_question(question)
    return {"answer": answer}


@app.get("/health")
async def health():
    return {"status": "ok"}

# Mount static files LAST so API routes (/scan, /ask, /health) take priority
app.mount("/", StaticFiles(directory="static", html=True), name="static")
