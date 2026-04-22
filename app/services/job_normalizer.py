from __future__ import annotations

from app.models.job_role import JobRole
from app.models.personality import PersonalityWeights
from app.models.retrieved_job import RetrievedJob


def normalize_jobs(retrieved_jobs: list[RetrievedJob]) -> list[JobRole]:
    normalized: list[JobRole] = []
    for job in retrieved_jobs:
        normalized.append(
            JobRole(
                id=job.external_id,
                title=job.title,
                required_skills=job.required_skills,
                preferred_education=job.preferred_education,
                personality_weights=job.personality_weights
                or PersonalityWeights(
                    analytical=0.5,
                    social=0.5,
                    structured=0.5,
                    creative=0.5,
                    leadership=0.5,
                ),
                related_interests=job.related_interests,
            )
        )
    return normalized
