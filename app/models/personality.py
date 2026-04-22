from app.models.candidate import PersonalityAnswers, PersonalityProfile


class PersonalityWeights(PersonalityProfile):
    """Role-level personality weighting alias used by matching and tests."""


__all__ = ["PersonalityAnswers", "PersonalityProfile", "PersonalityWeights"]
