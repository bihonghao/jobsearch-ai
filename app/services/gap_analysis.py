from __future__ import annotations

from app.models.candidate import CandidateProfile
from app.models.job_role import JobRole
from app.models.recommendation import GapAnalysis

COURSE_CATALOG = {
    "python": "Python for Everybody",
    "sql": "SQL for Data Analysis",
    "machine learning": "Intro to Machine Learning",
    "project management": "Google Project Management Certificate",
    "figma": "UI/UX Design in Figma",
    "cloud": "Cloud Practitioner Essentials",
    "aws": "AWS Cloud Technical Essentials",
    "docker": "Docker Essentials",
    "kubernetes": "Kubernetes for Developers",
    "sales": "B2B Sales Foundations",
    "marketing": "Digital Marketing Fundamentals",
    "tableau": "Data Visualization with Tableau",
    "statistics": "Statistics for Data Science",
    "agile": "Agile with Atlassian Jira",
}


def analyze_skill_gaps(candidate: CandidateProfile, role: JobRole) -> GapAnalysis:
    candidate_skills = {skill.lower() for skill in candidate.skills}
    missing = [skill for skill in role.required_skills if skill.lower() not in candidate_skills]

    questions = [
        (
            f"Have you used comparable tools or workflows related to '{skill}' "
            "in projects, volunteering, or coursework?"
        )
        for skill in missing
    ]

    transferable_prompt = (
        "What transferable experience do you have (leadership, stakeholder communication, "
        "cross-team delivery) that could support this role?"
    )
    if missing:
        questions.append(transferable_prompt)

    courses = [COURSE_CATALOG[skill.lower()] for skill in missing if skill.lower() in COURSE_CATALOG]

    return GapAnalysis(
        missing_skills=missing,
        follow_up_questions=questions,
        recommended_courses=courses,
    )
