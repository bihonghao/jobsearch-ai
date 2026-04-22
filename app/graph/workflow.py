from __future__ import annotations

import re
from typing import TypedDict

from langgraph.graph import END, StateGraph

from app.models.candidate import CandidateInput, CandidateProfile, PersonalityProfile
from app.models.job_role import JobRole
from app.models.recommendation import GapAnalysis, JobRecommendation, Recommendation
from app.models.retrieved_job import RetrievedJob
from app.services.gap_analysis import analyze_skill_gaps
from app.services.job_normalizer import normalize_jobs
from app.services.job_retrieval import get_job_source
from app.services.matcher import score_role_match
from app.services.parser import parse_candidate_profile
from app.services.personality import score_personality


class WorkflowState(TypedDict, total=False):
    candidate_input: CandidateInput
    candidate_profile: CandidateProfile
    job_search_queries: list[str]
    retrieved_jobs: list[RetrievedJob]
    normalized_jobs: list[JobRole]
    ranked_jobs: list[tuple[JobRole, float]]
    gap_analysis_by_role: dict[str, GapAnalysis]
    recommendation: Recommendation


def _normalize_target_role(value: str) -> str:
    collapsed = re.sub(r"[^a-z0-9]+", " ", value.lower())
    return " ".join(collapsed.split())


def _filter_target_roles(roles: list[JobRole], target_roles: list[str]) -> list[JobRole]:
    if not target_roles:
        return roles

    normalized_targets = {_normalize_target_role(role) for role in target_roles}
    filtered = [
        role
        for role in roles
        if _normalize_target_role(role.title) in normalized_targets or _normalize_target_role(role.id) in normalized_targets
    ]
    return filtered or roles


def _transferable_skills_bonus(profile: CandidateProfile, role: JobRole) -> float:
    transferable = {"communication", "leadership", "project management", "customer support", "sales"}
    cskills = {s.lower() for s in profile.skills}
    rskills = {s.lower() for s in role.required_skills}
    overlap = len((cskills & transferable) & rskills)
    return min(0.1, overlap * 0.03)


def parse_candidate_input(state: WorkflowState) -> WorkflowState:
    candidate_input = state["candidate_input"]
    neutral = PersonalityProfile(analytical=0.5, social=0.5, structured=0.5, creative=0.5, leadership=0.5)
    profile = parse_candidate_profile(
        resume_text=candidate_input.resume_text,
        profile_text=candidate_input.profile_text,
        personality=neutral,
    )
    return {"candidate_profile": profile}


def score_personality_node(state: WorkflowState) -> WorkflowState:
    profile = state["candidate_profile"]
    candidate_input = state["candidate_input"]
    personality = score_personality(candidate_input.personality_answers)
    return {
        "candidate_profile": CandidateProfile(
            skills=profile.skills,
            experience_years=profile.experience_years,
            education=profile.education,
            interests=profile.interests,
            personality=personality,
        )
    }


def generate_job_search_queries(state: WorkflowState) -> WorkflowState:
    profile = state["candidate_profile"]
    candidate_input = state["candidate_input"]

    titles = list(dict.fromkeys(candidate_input.target_roles))
    related = [f"{interest} jobs" for interest in profile.interests[:3]]
    transferable = [f"{skill} transferable career" for skill in profile.skills[:3]]

    queries = titles + related + transferable
    if not queries:
        queries = ["entry level data roles", "operations analyst", "product roles"]
    return {"job_search_queries": queries}


def retrieve_jobs(state: WorkflowState) -> WorkflowState:
    queries = state.get("job_search_queries", [])
    source = get_job_source()
    retrieved = source.retrieve_jobs(queries)
    return {"retrieved_jobs": retrieved}


def normalize_jobs_node(state: WorkflowState) -> WorkflowState:
    retrieved = state.get("retrieved_jobs", [])
    roles = normalize_jobs(retrieved)
    roles = _filter_target_roles(roles, state["candidate_input"].target_roles)
    return {"normalized_jobs": roles}


def rank_jobs(state: WorkflowState) -> WorkflowState:
    profile = state["candidate_profile"]
    roles = state.get("normalized_jobs", [])

    ranked: list[tuple[JobRole, float]] = []
    for role in roles:
        score = score_role_match(profile, role) + _transferable_skills_bonus(profile, role)
        ranked.append((role, round(min(1.0, score), 4)))

    ranked.sort(key=lambda item: item[1], reverse=True)
    return {"ranked_jobs": ranked}


def analyze_gaps(state: WorkflowState) -> WorkflowState:
    profile = state["candidate_profile"]
    ranked = state.get("ranked_jobs", [])[:3]
    gaps = {role.id: analyze_skill_gaps(profile, role) for role, _ in ranked}
    return {"gap_analysis_by_role": gaps}


def generate_recommendations(state: WorkflowState) -> WorkflowState:
    profile = state["candidate_profile"]
    ranked = state.get("ranked_jobs", [])[:3]
    gaps = state.get("gap_analysis_by_role", {})

    top_jobs: list[JobRecommendation] = []
    for role, score in ranked:
        matched_skill_count = len({skill.lower() for skill in profile.skills} & {skill.lower() for skill in role.required_skills})
        rationale = (
            f"Matched by skills ({matched_skill_count}/{len(role.required_skills)}) "
            "with personality, interests, and transferable skills alignment."
        )
        top_jobs.append(
            JobRecommendation(
                role_id=role.id,
                role_title=role.title,
                score=score,
                rationale=rationale,
                gap_analysis=gaps.get(role.id) or analyze_skill_gaps(profile, role),
            )
        )

    return {"recommendation": Recommendation(candidate_profile=profile, top_jobs=top_jobs)}


def build_workflow():
    graph = StateGraph(WorkflowState)
    graph.add_node("parse_candidate_input", parse_candidate_input)
    graph.add_node("score_personality", score_personality_node)
    graph.add_node("generate_job_search_queries", generate_job_search_queries)
    graph.add_node("retrieve_jobs", retrieve_jobs)
    graph.add_node("normalize_jobs", normalize_jobs_node)
    graph.add_node("rank_jobs", rank_jobs)
    graph.add_node("analyze_gaps", analyze_gaps)
    graph.add_node("generate_recommendations", generate_recommendations)

    graph.set_entry_point("parse_candidate_input")
    graph.add_edge("parse_candidate_input", "score_personality")
    graph.add_edge("score_personality", "generate_job_search_queries")
    graph.add_edge("generate_job_search_queries", "retrieve_jobs")
    graph.add_edge("retrieve_jobs", "normalize_jobs")
    graph.add_edge("normalize_jobs", "rank_jobs")
    graph.add_edge("rank_jobs", "analyze_gaps")
    graph.add_edge("analyze_gaps", "generate_recommendations")
    graph.add_edge("generate_recommendations", END)

    return graph.compile()


WORKFLOW_APP = build_workflow()


def run_workflow(candidate_input: CandidateInput) -> Recommendation:
    result = WORKFLOW_APP.invoke({"candidate_input": candidate_input})
    return result["recommendation"]
