from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import HTMLResponse

from app.graph.workflow import run_workflow
from app.models.candidate import CandidateInput, PersonalityAnswers
from app.models.recommendation import Recommendation
from app.models.upload import UploadResponse
from app.services.file_parser import FileParseError, parse_personality_results_upload, parse_resume_upload
from app.services.storage import save_personality_results, save_resume_upload

router = APIRouter()


UPLOAD_PAGE_HTML = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>JobSearch AI Upload</title>
    <style>
      body { font-family: Arial, sans-serif; max-width: 860px; margin: 2rem auto; padding: 0 1rem; }
      form { display: grid; gap: 0.8rem; border: 1px solid #ddd; padding: 1rem; border-radius: 8px; }
      textarea { min-height: 90px; }
      button { width: 180px; padding: 0.6rem; }
      pre { background: #111; color: #eaeaea; padding: 1rem; overflow: auto; border-radius: 8px; }
    </style>
  </head>
  <body>
    <h1>JobSearch AI</h1>
    <p>Upload your resume and personality results to run analysis.</p>
    <form id="upload-form">
      <label>Resume file (.txt, .pdf, .docx): <input name="resume_file" type="file" required /></label>
      <label>Personality results JSON: <input name="personality_results_file" type="file" required /></label>
      <label>Profile text (optional): <textarea name="profile_text" placeholder="LinkedIn summary or interests"></textarea></label>
      <button type="submit">Analyze Upload</button>
    </form>

    <h2>Result</h2>
    <pre id="result">Submit files to see analysis output...</pre>

    <script>
      const form = document.getElementById('upload-form');
      const result = document.getElementById('result');

      form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const data = new FormData(form);
        result.textContent = 'Analyzing...';
        try {
          const response = await fetch('/analyze-upload', { method: 'POST', body: data });
          const payload = await response.json();
          result.textContent = JSON.stringify(payload, null, 2);
        } catch (error) {
          result.textContent = `Request failed: ${error}`;
        }
      });
    </script>
  </body>
</html>
"""


@router.get("/", response_class=HTMLResponse)
def home() -> str:
    return UPLOAD_PAGE_HTML


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/analyze", response_model=Recommendation)
def analyze(candidate_input: CandidateInput) -> Recommendation:
    return run_workflow(candidate_input)


@router.post("/analyze-upload", response_model=Recommendation)
async def analyze_upload(
    resume_file: UploadFile = File(...),
    personality_results_file: UploadFile = File(...),
    profile_text: str | None = Form(default=None),
) -> Recommendation:
    resume_content = await resume_file.read()
    personality_content = await personality_results_file.read()

    if Path(personality_results_file.filename or "").suffix.lower() != ".json":
        raise HTTPException(status_code=400, detail="personality_results_file must be a .json file")

    try:
        resume_text = parse_resume_upload(resume_file.filename or "resume.txt", resume_content)
        personality_answers = parse_personality_results_upload(personality_content)
    except FileParseError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    candidate_input = CandidateInput(
        resume_text=resume_text,
        profile_text=(profile_text or "No additional profile text provided."),
        personality_answers=personality_answers,
        target_roles=[],
    )
    return run_workflow(candidate_input)


@router.post("/uploads/resume", response_model=UploadResponse)
async def upload_resume(file: UploadFile = File(...)) -> UploadResponse:
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded resume file is empty")

    try:
        saved_path = save_resume_upload(file.filename or "resume.txt", content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return UploadResponse(upload_type="resume", file_path=str(saved_path), message="Resume uploaded successfully")


@router.post("/uploads/personality", response_model=UploadResponse)
def upload_personality_results(answers: PersonalityAnswers) -> UploadResponse:
    saved_path = save_personality_results(answers)
    return UploadResponse(
        upload_type="personality",
        file_path=str(saved_path),
        message="Personality results uploaded successfully",
    )
