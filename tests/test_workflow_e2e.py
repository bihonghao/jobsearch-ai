from app.graph.workflow import run_workflow
from app.models.candidate import CandidateInput, PersonalityAnswers


def test_langgraph_workflow_runs_end_to_end() -> None:
    candidate_input = CandidateInput(
        resume_text="4 years building python data analytics dashboards and machine learning features",
        profile_text="Interested in AI, finance, and product strategy roles",
        personality_answers=PersonalityAnswers(
            analytical=5,
            social=3,
            structured=4,
            creative=4,
            leadership=4,
        ),
        target_roles=["data scientist"],
    )

    result = run_workflow(candidate_input)

    assert result.candidate_profile.skills
    assert len(result.top_jobs) <= 3
    if result.top_jobs:
        top = result.top_jobs[0]
        assert isinstance(top.rationale, str)
        assert top.gap_analysis is not None
