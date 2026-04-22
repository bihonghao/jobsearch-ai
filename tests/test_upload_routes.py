from __future__ import annotations

import json

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_upload_page_loads_successfully() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "JobSearch AI" in response.text
    assert "resume_file" in response.text


def test_analyze_upload_txt_and_personality_answers_json() -> None:
    files = {
        "resume_file": ("resume.txt", b"5 years python api sql leadership experience", "text/plain"),
        "personality_results_file": (
            "personality.json",
            json.dumps(
                {
                    "personality_answers": {
                        "analytical": 5,
                        "social": 3,
                        "structured": 4,
                        "creative": 4,
                        "leadership": 4,
                    }
                }
            ).encode("utf-8"),
            "application/json",
        ),
    }

    response = client.post("/analyze-upload", files=files, data={"profile_text": "Interested in data and ai."})

    assert response.status_code == 200
    payload = response.json()
    assert "candidate_profile" in payload
    assert "top_jobs" in payload


def test_analyze_upload_pdf_and_disc_json(monkeypatch) -> None:
    from app.services import file_parser

    def _fake_extract_pdf_text(_: bytes) -> str:
        return "4 years python machine learning communication"

    monkeypatch.setattr(file_parser, "_extract_pdf_text", _fake_extract_pdf_text)

    files = {
        "resume_file": ("resume.pdf", b"%PDF-1.4 fake content", "application/pdf"),
        "personality_results_file": (
            "personality.json",
            json.dumps({"disc_results": {"D": 80, "I": 70, "S": 60, "C": 90}}).encode("utf-8"),
            "application/json",
        ),
    }

    response = client.post("/analyze-upload", files=files)

    assert response.status_code == 200
    assert isinstance(response.json().get("top_jobs"), list)


def test_analyze_upload_invalid_resume_file_type() -> None:
    files = {
        "resume_file": ("resume.exe", b"binary", "application/octet-stream"),
        "personality_results_file": (
            "personality.json",
            json.dumps(
                {
                    "personality_answers": {
                        "analytical": 5,
                        "social": 3,
                        "structured": 4,
                        "creative": 4,
                        "leadership": 4,
                    }
                }
            ).encode("utf-8"),
            "application/json",
        ),
    }

    response = client.post("/analyze-upload", files=files)

    assert response.status_code == 400
    assert "Unsupported resume file type" in response.json()["detail"]


def test_analyze_upload_invalid_json_schema() -> None:
    files = {
        "resume_file": ("resume.txt", b"Python SQL analytics teamwork", "text/plain"),
        "personality_results_file": (
            "personality.json",
            json.dumps({"bad_schema": {"x": 1}}).encode("utf-8"),
            "application/json",
        ),
    }

    response = client.post("/analyze-upload", files=files)

    assert response.status_code == 400
    assert "Unsupported personality schema" in response.json()["detail"]
