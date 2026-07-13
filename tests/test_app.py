import asyncio

import httpx

from src import app as app_module


def test_scan_endpoint_returns_translation_and_explanation(monkeypatch):
    monkeypatch.setattr(app_module, "extract_text", lambda path: "hello")
    monkeypatch.setattr(
        app_module,
        "translate_and_explain",
        lambda text, target_language: {
            "translation": "hola",
            "explanation": "A greeting",
        },
    )

    async def run_request():
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app_module.app),
            base_url="http://testserver",
        ) as client:
            return await client.post(
                "/scan",
                data={"target_language": "es"},
                files={"file": ("sample.png", b"fake-image-bytes", "image/png")},
            )

    response = asyncio.run(run_request())

    assert response.status_code == 200
    assert response.json() == {
        "original_text": "hello",
        "translation": "hola",
        "explanation": "A greeting",
    }


def test_scan_endpoint_rejects_non_image_files():
    async def run_request():
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app_module.app),
            base_url="http://testserver",
        ) as client:
            return await client.post(
                "/scan",
                data={"target_language": "es"},
                files={"file": ("sample.txt", b"not-an-image", "text/plain")},
            )

    response = asyncio.run(run_request())

    assert response.status_code == 400


def test_scan_endpoint_rejects_large_files():
    async def run_request():
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app_module.app),
            base_url="http://testserver",
        ) as client:
            file_content = b"a" * (5 * 1024 * 1024 + 1)
            return await client.post(
                "/scan",
                data={"target_language": "es"},
                files={"file": ("sample.png", file_content, "image/png")},
            )

    response = asyncio.run(run_request())

    assert response.status_code == 400


def test_scan_endpoint_rejects_empty_target_language():
    async def run_request():
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app_module.app),
            base_url="http://testserver",
        ) as client:
            return await client.post(
                "/scan",
                data={"target_language": "  "},
                files={"file": ("sample.png", b"fake-image-bytes", "image/png")},
            )

    response = asyncio.run(run_request())

    assert response.status_code == 400


def test_ask_endpoint_rejects_empty_question():
    async def run_request():
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app_module.app),
            base_url="http://testserver",
        ) as client:
            return await client.post(
                "/ask",
                json={"question": "  "},
            )

    response = asyncio.run(run_request())

    assert response.status_code == 400
