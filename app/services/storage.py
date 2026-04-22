from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from app.models.candidate import PersonalityAnswers

UPLOAD_ROOT = Path(__file__).resolve().parent.parent / "data" / "uploads"
RESUME_DIR = UPLOAD_ROOT / "resumes"
PERSONALITY_DIR = UPLOAD_ROOT / "personality"
ALLOWED_RESUME_EXTENSIONS = {".txt", ".pdf", ".doc", ".docx"}


def _ensure_upload_dirs() -> None:
    RESUME_DIR.mkdir(parents=True, exist_ok=True)
    PERSONALITY_DIR.mkdir(parents=True, exist_ok=True)


def save_resume_upload(filename: str, content: bytes) -> Path:
    _ensure_upload_dirs()
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_RESUME_EXTENSIONS:
        raise ValueError("Unsupported resume file type. Use .txt, .pdf, .doc, or .docx")

    target = RESUME_DIR / f"{uuid4().hex}_{Path(filename).name}"
    target.write_bytes(content)
    return target


def save_personality_results(answers: PersonalityAnswers) -> Path:
    _ensure_upload_dirs()
    target = PERSONALITY_DIR / f"{uuid4().hex}.json"
    payload = {"saved_at": datetime.now(tz=timezone.utc).isoformat(), "answers": answers.model_dump()}
    target.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return target
