from __future__ import annotations

from pydantic import BaseModel, Field

from app.models.personality import PersonalityWeights


class RetrievedJob(BaseModel):
    """Normalized shape from any job source before role normalization."""

    source: str = "local_seed"
    external_id: str
    title: str
    required_skills: list[str] = Field(default_factory=list)
    preferred_education: list[str] = Field(default_factory=list)
    related_interests: list[str] = Field(default_factory=list)
    personality_weights: PersonalityWeights | None = None
