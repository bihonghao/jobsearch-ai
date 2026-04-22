from app.models.candidate import CandidateProfile, PersonalityProfile
from app.services.matcher import load_job_roles, rank_roles


def test_rank_roles_returns_scored_roles() -> None:
    roles = load_job_roles()
    candidate = CandidateProfile(
        skills=["python", "sql", "machine learning", "statistics", "data analysis"],
        experience_years=3,
        education=["master"],
        interests=["ai", "finance"],
        personality=PersonalityProfile(
            analytical=1.0,
            social=0.3,
            structured=0.7,
            creative=0.6,
            leadership=0.4,
        ),
    )

    ranked = rank_roles(candidate, roles)
    assert len(ranked) >= 3
    top_role, score = ranked[0]
    assert top_role.title in {"Data Scientist", "Data Analyst"}
    assert 0.0 <= score <= 1.0
