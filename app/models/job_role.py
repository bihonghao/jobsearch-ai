from __future__ import annotations

from pydantic import BaseModel, Field

from app.models.candidate import PersonalityProfile


class JobRole(BaseModel):
    id: str
    title: str
    required_skills: list[str] = Field(default_factory=list)
    preferred_education: list[str] = Field(default_factory=list)
    personality_weights: PersonalityProfile
    related_interests: list[str] = Field(default_factory=list)
