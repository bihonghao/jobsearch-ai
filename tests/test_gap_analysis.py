from app.models.candidate import CandidateProfile, PersonalityProfile
from app.models.job_role import JobRole
from app.models.recommendation import GapAnalysis
from app.services.gap_analysis import analyze_skill_gaps


def test_gap_analysis_is_case_insensitive() -> None:
    candidate = CandidateProfile(
        skills=["Python", "SQL"],
        experience_years=2,
        education=["bachelor"],
        interests=["ai"],
        personality=PersonalityProfile(
            analytical=0.8,
            social=0.4,
            structured=0.7,
            creative=0.6,
            leadership=0.5,
        ),
    )
    role = JobRole(
        id="role_1",
        title="Data Scientist",
        required_skills=["python", "sql", "machine learning"],
        preferred_education=["bachelor"],
        personality_weights=PersonalityProfile(
            analytical=0.9,
            social=0.3,
            structured=0.6,
            creative=0.7,
            leadership=0.5,
        ),
        related_interests=["ai"],
    )

    result: GapAnalysis = analyze_skill_gaps(candidate, role)

    assert result.missing_skills == ["machine learning"]
    assert any("machine learning" in question for question in result.follow_up_questions)
