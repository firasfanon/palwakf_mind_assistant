from palwakf_mind_assistant.domain.models import PlanningRequest
from palwakf_mind_assistant.services.planning_engine import PlanningEngine


def test_plan_requires_human_review_and_no_mutation():
    request = PlanningRequest(
        project_id="PALWAKF_MIND_ASSISTANT",
        goal="Implement change",
    )
    result = PlanningEngine().plan(
        request,
        source_refs=("drive:state",),
        skill_ids=("SKILL",),
    )
    assert result.graph.mutation_mode == "READ_ONLY"
    assert result.approval_required is True
    assert any(node.requires_approval for node in result.graph.nodes)
