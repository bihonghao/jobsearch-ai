from __future__ import annotations

import re

from app.models.candidate import CandidateProfile, PersonalityProfile

KNOWN_SKILLS = {
    "python",
    "sql",
    "excel",
    "machine learning",
    "data analysis",
    "communication",
    "project management",
    "figma",
    "javascript",
    "react",
    "cloud",
    "aws",
    "docker",
    "kubernetes",
    "sales",
    "marketing",
    "content writing",
    "customer support",
    "public speaking",
    "leadership",
    "tableau",
    "power bi",
    "statistics",
    "product strategy",
    "agile",
}

EDUCATION_KEYWORDS = {
    "bachelor",
    "master",
    "phd",
    "mba",
    "bootcamp",
    "associate",
}

INTEREST_KEYWORDS = {
    "ai",
    "automation",
    "finance",
    "healthcare",
    "design",
    "education",
    "gaming",
    "sustainability",
    "startups",
}


def _contains_phrase(text: str, phrase: str) -> bool:
    """Return True when a phrase appears as whole words.

    This supports common separators (spaces, hyphens, slashes) between
    multi-word phrases while still preventing partial-token matches.
    """

    parts = [re.escape(part) for part in phrase.strip().split() if part]
    if not parts:
        return False

    separator = r"(?:[\s\-/]+)"
    joined = separator.join(parts)
    pattern = rf"(?<!\w){joined}(?!\w)"
    return re.search(pattern, text, flags=re.IGNORECASE) is not None


def _extract_skills(text: str) -> list[str]:
    matches = [skill for skill in KNOWN_SKILLS if _contains_phrase(text, skill)]
    return sorted(set(matches))


def _extract_education(text: str) -> list[str]:
    found = [keyword for keyword in EDUCATION_KEYWORDS if _contains_phrase(text, keyword)]
    return sorted(set(found))


def _extract_interests(text: str) -> list[str]:
    found = [keyword for keyword in INTEREST_KEYWORDS if _contains_phrase(text, keyword)]
    return sorted(set(found))


def _extract_experience_years(text: str) -> int:
    patterns = [
        r"(\d+)\+?\s+years?",
        r"(\d+)\+?\s+yrs?",
    ]
    years: list[int] = []
    for pattern in patterns:
        years.extend(int(match) for match in re.findall(pattern, text.lower()))
    return max(years) if years else 0


def parse_candidate_profile(
    resume_text: str,
    profile_text: str,
    personality: PersonalityProfile,
) -> CandidateProfile:
    combined = f"{resume_text}\n{profile_text}"
    return CandidateProfile(
        skills=_extract_skills(combined),
        experience_years=_extract_experience_years(combined),
        education=_extract_education(combined),
        interests=_extract_interests(combined),
        personality=personality,
    )
