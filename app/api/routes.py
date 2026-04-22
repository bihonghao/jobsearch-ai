from __future__ import annotations

from fastapi import APIRouter

from app.graph.workflow import run_workflow
from app.models.candidate import CandidateInput
from app.models.recommendation import Recommendation

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/analyze", response_model=Recommendation)
def analyze(candidate_input: CandidateInput) -> Recommendation:
    return run_workflow(candidate_input)
