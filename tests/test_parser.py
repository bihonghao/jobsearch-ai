from app.models.candidate import PersonalityProfile
from app.services.parser import parse_candidate_profile


def test_parser_avoids_partial_word_skill_matches() -> None:
    profile = parse_candidate_profile(
        resume_text="Built sequel data integrations and api tooling.",
        profile_text="Interested in automation and analytics.",
        personality=PersonalityProfile(
            analytical=0.5,
            social=0.5,
            structured=0.5,
            creative=0.5,
            leadership=0.5,
        ),
    )

    assert "sql" not in profile.skills
