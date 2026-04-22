from __future__ import annotations

import json
from pathlib import Path

from app.models.candidate import CandidateProfile
from app.models.job_role import JobRole

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "job_roles.json"


def load_job_roles(path: Path = DATA_PATH) -> list[JobRole]:
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    return [JobRole.model_validate(role) for role in payload]


def _personality_similarity(candidate: CandidateProfile, role: JobRole) -> float:
    c = candidate.personality
    r = role.personality_weights
    deltas = [
        abs(c.analytical - r.analytical),
        abs(c.social - r.social),
        abs(c.structured - r.structured),
        abs(c.creative - r.creative),
        abs(c.leadership - r.leadership),
    ]
    return 1.0 - (sum(deltas) / len(deltas))


def score_role_match(candidate: CandidateProfile, role: JobRole) -> float:
    candidate_skills = {skill.lower() for skill in candidate.skills}
    required = {skill.lower() for skill in role.required_skills}
    skill_score = (len(candidate_skills & required) / len(required)) if required else 0.0
    personality_score = _personality_similarity(candidate, role)

    candidate_interests = {interest.lower() for interest in candidate.interests}
    role_interests = {interest.lower() for interest in role.related_interests}
    interest_alignment = (len(candidate_interests & role_interests) / len(role_interests)) if role_interests else 0.0

    return round((0.6 * skill_score) + (0.3 * personality_score) + (0.1 * interest_alignment), 4)


def rank_roles(candidate: CandidateProfile, roles: list[JobRole]) -> list[tuple[JobRole, float]]:
    scored = [(role, score_role_match(candidate, role)) for role in roles]
    return sorted(scored, key=lambda item: item[1], reverse=True)
