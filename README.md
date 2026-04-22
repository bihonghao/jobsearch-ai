# JobSearch AI (MVP)

API-first MVP that analyzes a candidate profile and recommends top-fit jobs.

## Features
- Accepts resume text, LinkedIn/profile text, and personality quiz answers.
- Extracts skills, experience, education, and interests using heuristic parsing.
- Scores personality across: analytical, social, structured, creative, leadership.
- Matches candidate to seeded job roles using skill overlap + personality similarity.
- Performs gap analysis, asks follow-up questions, and recommends courses.
- Returns top 3 job recommendations.
- Uses a simple LangGraph workflow and FastAPI API endpoints.

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

## API
### `GET /health`
Returns service health.

### `POST /analyze`
Request body:
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

Response includes:
- extracted candidate profile (skills, experience, education, interests, personality)
- top 3 job recommendations
- optional `target_roles` accepts either role titles or role ids
- score + rationale
- missing skills
- follow-up questions for hidden/transferable skills
- course suggestions for missing skills

## Tests
```bash
pytest -q
```
