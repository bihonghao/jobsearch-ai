from app.graph.workflow import _filter_target_roles
from app.models.job_role import JobRole
from app.models.personality import PersonalityWeights


def _role(role_id: str, title: str) -> JobRole:
    return JobRole(
        id=role_id,
        title=title,
        required_skills=["python"],
        preferred_education=["bachelor"],
        personality_weights=PersonalityWeights(
            analytical=0.8,
            social=0.3,
            structured=0.6,
            creative=0.4,
            leadership=0.5,
        ),
        related_interests=["ai"],
    )


def test_filter_target_roles_matches_on_id_and_title() -> None:
    roles = [_role("data_scientist", "Data Scientist"), _role("product_manager", "Product Manager")]

    by_id = _filter_target_roles(roles, ["data_scientist"])
    assert len(by_id) == 1
    assert by_id[0].title == "Data Scientist"

    by_title = _filter_target_roles(roles, ["product manager"])
    assert len(by_title) == 1
    assert by_title[0].id == "product_manager"

    by_hyphenated = _filter_target_roles(roles, ["data-scientist"])
    assert len(by_hyphenated) == 1
    assert by_hyphenated[0].id == "data_scientist"


def test_filter_target_roles_falls_back_when_no_match() -> None:
    roles = [_role("data_scientist", "Data Scientist")]

    result = _filter_target_roles(roles, ["Unknown Role"])

    assert result == roles
