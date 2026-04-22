from __future__ import annotations

from app.models.candidate import PersonalityAnswers, PersonalityProfile


def score_personality(answers: PersonalityAnswers) -> PersonalityProfile:
    """Normalize 1-5 responses to 0.0-1.0 scores."""

    def normalize(value: int) -> float:
        return round((value - 1) / 4, 3)

    return PersonalityProfile(
        analytical=normalize(answers.analytical),
        social=normalize(answers.social),
        structured=normalize(answers.structured),
        creative=normalize(answers.creative),
        leadership=normalize(answers.leadership),
    )
