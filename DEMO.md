# SignSpeak live demo script

## Before you demo

Make sure all three services are up at the same time:

- Ollama is running: `ollama list`
- LibreTranslate is running on port `5000`
- FastAPI is running with: `uvicorn src.app:app --reload`

If any one of these is down, the scan flow will not work properly.

## Demo walkthrough

1. Open the page and show the “00 About this assistant” panel first. Briefly explain that this is a GenAI-powered accessibility assistant built for the FIFA World Cup 2026 Smart Stadiums challenge.
2. Upload a simple sign image such as an “EXIT THIS WAY” test image and switch the target language to German or Spanish. Let the split-flap results reveal the original text, translation, and explanation.
3. Upload a more stylized or graphic sign such as a “TICKETS HERE” style image. Point out that the OCR is handling real-world signage, not just plain text.
4. Switch the target language to Arabic or Hindi. This highlights the multilingual support and the right-to-left layout behavior.
5. In the “Ask a question” section, type a natural question such as “where can I get food” to show the FAQ assistant answering from the venue knowledge base.
6. Optional: ask an off-topic question such as “what is the weather like?” to show that the assistant declines gracefully instead of hallucinating.

## What to have ready

Have these local files saved and ready to upload:

- A plain test image with text like “EXIT THIS WAY”
- A stylized or graphic sign image such as “TICKETS HERE”
- A second image with a different layout or font if you want to show OCR robustness

If a scan takes a few seconds, say this out loud: “The model is doing local inference on-device, so this can take a moment; it is not a bug.”

## If something breaks

- If `/scan` fails, check that Ollama, LibreTranslate, and the FastAPI server are all running.
- If translation seems off for a specific language, mention that it is a known limitation of the current setup rather than a crash.
