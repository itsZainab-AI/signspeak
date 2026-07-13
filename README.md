# SignSpeak

SignSpeak is a Generative AI-powered multilingual accessibility assistant for stadium visitors, using a locally-hosted large language model (Google's Gemma 2, 2B parameters, served through Ollama) to generate real-time explanations and natural-language answers to fan questions.

## Problem Statement Alignment

This project directly addresses the Accessibility and Multilingual Assistance pillars of the FIFA World Cup 2026 Smart Stadiums challenge.

It provides two core features:

1. Scan-and-translate signage using OCR, LibreTranslate, and LLM-generated explanations.
2. Natural-language Q&A over a stadium FAQ knowledge base using the same local LLM.

## Architecture Overview

```text
Image Flow
image
  -> OCR (Tesseract, with binarization preprocessing for stylized signage)
  -> LibreTranslate (translation) + Ollama/Gemma 2 (explanation)
  -> combined JSON response

Question Flow
question
  -> Ollama/Gemma 2 (matches against FAQ)
  -> FAQ lookup
  -> answer
```

## Tech Stack

- FastAPI for the backend API
- Tesseract OCR via pytesseract with Pillow-based preprocessing
- LibreTranslate (self-hosted)
- Ollama running Gemma 2 (2B)
- Vanilla HTML/CSS/JS frontend
- pytest and httpx for automated testing

## Setup Instructions

1. Install Tesseract OCR on your machine and ensure the `tesseract` binary is available in your PATH.
2. Install Ollama and pull the model:

```bash
ollama pull gemma2:2b
```

3. Install LibreTranslate via pip and run it:

```bash
pip install libretranslate
libretranslate --port 5000
```

4. Install Python dependencies:

```bash
pip install -r requirements.txt
```

5. Start the FastAPI app:

```bash
uvicorn src.app:app --reload
```

6. Open the frontend in a browser:

```text
static/index.html
```

> Three services must be running simultaneously for `/scan` to work: Ollama, LibreTranslate, and FastAPI. Run them in three separate terminals.

## Evaluation Criteria Mapping

- Code Quality: modular src/ structure with custom exceptions for OCR and translation failures.
- Security: local-first processing, upload validation, input validation, and safe error responses.
- Efficiency: fully local/self-hosted deployment with no cloud API costs.
- Testing: 26 pytest tests across tests/, covering OCR (including stylized signage), translation with mocked external calls, knowledge base matching, and FastAPI endpoints. Run with:

```bash
python -m pytest tests/ -v
```

- Accessibility: multilingual OCR translation across 10 languages plus natural-language Q&A.

## Security

- The design is local-first, so no user data leaves the device during scan or Q&A workflows.
- Uploaded images are limited to 5MB and validated by content type before processing.
- Question and language inputs are validated to prevent empty or malformed requests.
- Error responses do not leak stack traces or internal file paths.
- No hardcoded secrets are required for the current local setup.

## Known Limitations and Design Decisions

- Translation quality varies by language pair and is strongest for widely spoken languages.
- The project was evaluated with llama3.1:8b for higher accuracy, but it was reverted to gemma2:2b to preserve acceptable response latency in a live demo context. This is a configurable tradeoff depending on deployment hardware.
- Regional dialect variation, such as Egyptian vs. Moroccan Arabic, is reflected in explanation tone through the LLM layer, while core translation uses standard language forms.
- OCR preprocessing uses binarization tuned for high-contrast stylized signage and may need adjustment for very low-contrast or handwritten signs.

## Supported Languages

- Arabic
- Chinese
- English
- French
- German
- Hindi
- Japanese
- Korean
- Portuguese
- Spanish
