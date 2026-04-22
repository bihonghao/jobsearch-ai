from __future__ import annotations

from pydantic import BaseModel, Field


class PersonalityAnswers(BaseModel):
    """Raw quiz answers from 1-5 for personality dimensions."""

    analytical: int = Field(ge=1, le=5)
    social: int = Field(ge=1, le=5)
    structured: int = Field(ge=1, le=5)
    creative: int = Field(ge=1, le=5)
    leadership: int = Field(ge=1, le=5)


class PersonalityProfile(BaseModel):
    """Normalized personality profile from 0.0 to 1.0."""

    analytical: float = Field(ge=0.0, le=1.0)
    social: float = Field(ge=0.0, le=1.0)
    structured: float = Field(ge=0.0, le=1.0)
    creative: float = Field(ge=0.0, le=1.0)
    leadership: float = Field(ge=0.0, le=1.0)


class CandidateInput(BaseModel):
    resume_text: str = Field(min_length=10)
    profile_text: str = Field(min_length=10)
    personality_answers: PersonalityAnswers
    target_roles: list[str] = Field(default_factory=list)


class CandidateProfile(BaseModel):
    skills: list[str] = Field(default_factory=list)
    experience_years: int = Field(default=0, ge=0)
    education: list[str] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)
    personality: PersonalityProfile
