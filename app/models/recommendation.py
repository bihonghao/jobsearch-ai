from __future__ import annotations

from pydantic import BaseModel, Field

from app.models.candidate import CandidateProfile


class GapAnalysis(BaseModel):
    missing_skills: list[str] = Field(default_factory=list)
    follow_up_questions: list[str] = Field(default_factory=list)
    recommended_courses: list[str] = Field(default_factory=list)


class JobRecommendation(BaseModel):
    role_id: str
    role_title: str
    score: float
    rationale: str
    gap_analysis: GapAnalysis


class Recommendation(BaseModel):
    candidate_profile: CandidateProfile
    top_jobs: list[JobRecommendation] = Field(default_factory=list)
