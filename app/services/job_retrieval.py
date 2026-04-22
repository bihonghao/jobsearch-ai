from __future__ import annotations

import os
from typing import Protocol

from app.models.retrieved_job import RetrievedJob
from app.services.matcher import load_job_roles


class JobSource(Protocol):
    def retrieve_jobs(self, queries: list[str]) -> list[RetrievedJob]:
        ...


class LocalSeedJobSource:
    def retrieve_jobs(self, queries: list[str]) -> list[RetrievedJob]:
        roles = load_job_roles()
        return [
            RetrievedJob(
                source="local_seed",
                external_id=role.id,
                title=role.title,
                required_skills=role.required_skills,
                preferred_education=role.preferred_education,
                related_interests=role.related_interests,
                personality_weights=role.personality_weights,
            )
            for role in roles
        ]


class LiveJobSource:
    """Placeholder live source for future API integration."""

    def __init__(self, api_url: str) -> None:
        self.api_url = api_url

    def retrieve_jobs(self, queries: list[str]) -> list[RetrievedJob]:
        # MVP: keep pluggable interface but fall back until API integration is configured.
        return []


def get_job_source() -> JobSource:
    api_url = os.getenv("JOBSEARCH_LIVE_API_URL", "").strip()
    if api_url:
        return LiveJobSource(api_url)
    return LocalSeedJobSource()
