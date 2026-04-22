# JobSearch AI (MVP)

API-first MVP for AI-driven job search recommendations.

## What it does
- Accepts resume text/profile text/personality answers via JSON (`POST /analyze`).
- Accepts resume + personality files via multipart upload (`POST /analyze-upload`).
- Uses **LangGraph** as the orchestration layer for parsing, scoring, retrieval, ranking, and gap analysis.
- Recommends top-fit jobs, missing skills, follow-up questions, and courses.
- Serves a minimal upload UI at `GET /`.

## Architecture overview
The backend uses a LangGraph pipeline with these nodes:
1. `parse_candidate_input`
2. `score_personality`
3. `generate_job_search_queries`
4. `retrieve_jobs`
5. `normalize_jobs`
6. `rank_jobs`
7. `analyze_gaps`
8. `generate_recommendations`

Implementation: `app/graph/workflow.py`.

## Job retrieval fallback behavior
`app/services/job_retrieval.py` provides a pluggable interface:
- `LiveJobSource` (placeholder for future API integration)
- `LocalSeedJobSource` (default fallback using `app/data/job_roles.json`)

If `JOBSEARCH_LIVE_API_URL` is not configured, the app uses local seeded roles.

## Project structure
```text
app/
  api/routes.py
  data/job_roles.json
  graph/workflow.py
  models/
  services/
  main.py
tests/
requirements.txt
```

## Quickstart
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Upload page usage
Open:
- `http://127.0.0.1:8000/`

The page includes:
- Resume upload field (`.txt`, `.pdf`, `.docx`)
- Personality results JSON upload field
- Optional profile text
- Submit button and response panel

## API

### `GET /health`
Health check.

### `POST /analyze`
JSON body (backward-compatible endpoint):
```json
{
  "resume_text": "3 years building Python APIs and data pipelines...",
  "profile_text": "Interested in AI and finance, worked with SQL and Tableau...",
  "personality_answers": {
    "analytical": 5,
    "social": 3,
    "structured": 4,
    "creative": 4,
    "leadership": 3
  },
  "target_roles": ["Data Scientist", "data_analyst"]
}
```

### `POST /analyze-upload`
`multipart/form-data` fields:
- `resume_file` (required): `.txt`, `.pdf`, `.docx`
- `personality_results_file` (required): `.json`
- `profile_text` (optional)

Supported personality JSON formats:

1) `personality_answers`
```json
{
  "personality_answers": {
    "analytical": 5,
    "social": 3,
    "structured": 4,
    "creative": 2,
    "leadership": 4
  }
}
```

2) `disc_results`
```json
{
  "disc_results": {
    "D": 80,
    "I": 70,
    "S": 65,
    "C": 90
  }
}
```

Example:
```bash
curl -X POST "http://127.0.0.1:8000/analyze-upload" \
  -F "resume_file=@./resume.pdf" \
  -F "personality_results_file=@./personality.json" \
  -F "profile_text=Interested in data products and AI"
```

### Optional upload-storage endpoints
- `POST /uploads/resume`
- `POST /uploads/personality`

Files are stored under `app/data/uploads/...`.

## Tests
```bash
pytest -q
```
