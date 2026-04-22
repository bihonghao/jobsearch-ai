from app.models.candidate import PersonalityAnswers
from app.services.personality import score_personality


def test_score_personality_normalization() -> None:
    profile = score_personality(
        PersonalityAnswers(
            analytical=5,
            social=1,
            structured=3,
            creative=4,
            leadership=2,
        )
    )

    assert profile.analytical == 1.0
    assert profile.social == 0.0
    assert profile.structured == 0.5
    assert profile.creative == 0.75
    assert profile.leadership == 0.25
