from __future__ import annotations

from typing import TypedDict

from langgraph.graph import END, StateGraph

from app.models.candidate import CandidateInput, CandidateProfile
from app.models.job_role import JobRole
from app.models.recommendation import JobRecommendation, Recommendation
from app.services.gap_analysis import analyze_skill_gaps
from app.services.matcher import load_job_roles, rank_roles
from app.services.parser import parse_candidate_profile
from app.services.personality import score_personality


class WorkflowState(TypedDict, total=False):
    candidate_input: CandidateInput
    candidate_profile: CandidateProfile
    recommendation: Recommendation


def _normalize_target_role(value: str) -> str:
    return " ".join(value.lower().split())


def _filter_target_roles(roles: list[JobRole], target_roles: list[str]) -> list[JobRole]:
    if not target_roles:
        return roles

    normalized_targets = {_normalize_target_role(role) for role in target_roles}
    filtered = [
        role
        for role in roles
        if _normalize_target_role(role.title) in normalized_targets or _normalize_target_role(role.id) in normalized_targets
    ]

    # Graceful fallback: if filter misses all roles, keep original list.
    return filtered or roles


def _parse_node(state: WorkflowState) -> WorkflowState:
    candidate_input = state["candidate_input"]
    personality = score_personality(candidate_input.personality_answers)
    profile = parse_candidate_profile(
        resume_text=candidate_input.resume_text,
        profile_text=candidate_input.profile_text,
        personality=personality,
    )
    return {"candidate_profile": profile}


def _match_node(state: WorkflowState) -> WorkflowState:
    profile = state["candidate_profile"]
    candidate_input = state["candidate_input"]

    roles = _filter_target_roles(load_job_roles(), candidate_input.target_roles)
    ranked = rank_roles(profile, roles)[:3]

    top_jobs: list[JobRecommendation] = []
    for role, score in ranked:
        gaps = analyze_skill_gaps(profile, role)
        matched_skill_count = len({skill.lower() for skill in profile.skills} & {skill.lower() for skill in role.required_skills})
        rationale = (
            f"Matched by skills ({matched_skill_count}/{len(role.required_skills)}) "
            "with personality and interest alignment."
        )
        top_jobs.append(
            JobRecommendation(
                role_id=role.id,
                role_title=role.title,
                score=score,
                rationale=rationale,
                gap_analysis=gaps,
            )
        )

    return {"recommendation": Recommendation(candidate_profile=profile, top_jobs=top_jobs)}


def build_workflow():
    graph = StateGraph(WorkflowState)
    graph.add_node("parse", _parse_node)
    graph.add_node("match", _match_node)
    graph.set_entry_point("parse")
    graph.add_edge("parse", "match")
    graph.add_edge("match", END)
    return graph.compile()


WORKFLOW_APP = build_workflow()


def run_workflow(candidate_input: CandidateInput) -> Recommendation:
    result = WORKFLOW_APP.invoke({"candidate_input": candidate_input})
    return result["recommendation"]
