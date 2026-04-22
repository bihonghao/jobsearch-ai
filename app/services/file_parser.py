from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path
from typing import Any

from docx import Document
from pydantic import ValidationError
from pypdf import PdfReader

from app.models.candidate import PersonalityAnswers

ALLOWED_RESUME_EXTENSIONS = {".txt", ".pdf", ".docx"}


class FileParseError(ValueError):
    """Raised when uploaded files cannot be parsed or validated."""


def parse_resume_upload(filename: str, content: bytes) -> str:
    if not content:
        raise FileParseError("Resume file is empty.")

    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_RESUME_EXTENSIONS:
        raise FileParseError("Unsupported resume file type. Use .txt, .pdf, or .docx")

    if suffix == ".txt":
        return _decode_text(content)
    if suffix == ".pdf":
        return _extract_pdf_text(content)
    return _extract_docx_text(content)


def parse_personality_results_upload(content: bytes) -> PersonalityAnswers:
    if not content:
        raise FileParseError("Personality results file is empty.")

    try:
        payload = json.loads(content.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise FileParseError("Personality results file must be valid UTF-8 JSON.") from exc

    if not isinstance(payload, dict):
        raise FileParseError("Personality results JSON must be an object.")

    if "personality_answers" in payload:
        try:
            return PersonalityAnswers.model_validate(payload["personality_answers"])
        except ValidationError as exc:
            raise FileParseError(
                "Invalid personality_answers schema. Expected analytical/social/structured/creative/leadership as 1-5 integers."
            ) from exc

    if "disc_results" in payload:
        return _disc_to_personality(payload["disc_results"])

    raise FileParseError("Unsupported personality schema. Provide either 'personality_answers' or 'disc_results'.")


def _decode_text(content: bytes) -> str:
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise FileParseError("TXT resume must be UTF-8 encoded.") from exc

    if not text.strip():
        raise FileParseError("Resume file has no readable text.")
    return text


def _extract_pdf_text(content: bytes) -> str:
    try:
        reader = PdfReader(BytesIO(content))
    except Exception as exc:  # noqa: BLE001
        raise FileParseError("Unable to read PDF resume file.") from exc

    extracted_pages = [(page.extract_text() or "").strip() for page in reader.pages]
    text = "\n".join(page for page in extracted_pages if page).strip()
    if not text:
        raise FileParseError("PDF resume has no extractable text.")
    return text


def _extract_docx_text(content: bytes) -> str:
    try:
        document = Document(BytesIO(content))
    except Exception as exc:  # noqa: BLE001
        raise FileParseError("Unable to read DOCX resume file.") from exc

    text = "\n".join(paragraph.text.strip() for paragraph in document.paragraphs if paragraph.text.strip()).strip()
    if not text:
        raise FileParseError("DOCX resume has no readable text.")
    return text


def _disc_to_personality(payload: Any) -> PersonalityAnswers:
    if not isinstance(payload, dict):
        raise FileParseError("disc_results must be an object with D, I, S, C scores.")

    required = {"D", "I", "S", "C"}
    if not required.issubset(payload):
        raise FileParseError("disc_results must include D, I, S, and C.")

    try:
        d = float(payload["D"])
        i = float(payload["I"])
        s = float(payload["S"])
        c = float(payload["C"])
    except (TypeError, ValueError) as exc:
        raise FileParseError("DISC scores must be numeric values.") from exc

    d5, i5, s5, c5 = [_normalize_disc_score(score) for score in (d, i, s, c)]
    return PersonalityAnswers(
        analytical=c5,
        social=i5,
        structured=s5,
        creative=max(1, min(5, round((i5 + d5) / 2))),
        leadership=d5,
    )


def _normalize_disc_score(score: float) -> int:
    if score < 0:
        raise FileParseError("DISC scores must be non-negative.")

    if score <= 5:
        mapped = score
    elif score <= 100:
        mapped = 1 + (score / 100) * 4
    else:
        raise FileParseError("DISC scores must be in the range 0-100 or 1-5.")

    return max(1, min(5, round(mapped)))
