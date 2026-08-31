from palwakf_mind_assistant.domain.models import EngineeringAdviceRequest
from palwakf_mind_assistant.services.engineering_advisor import EngineeringAdvisor


def test_advisor_never_marks_mutation_ready_from_fixture_state():
    request = EngineeringAdviceRequest(
        project_id="PALWAKF_MIND_ASSISTANT",
        request="change code",
    )
    result = EngineeringAdvisor().advise(request)
    assert result.next_safe_action.mutation_ready is False
    assert result.mutation_mode == "READ_ONLY"


def test_advisor_handles_second_profile_without_stale_assumption():
    request = EngineeringAdviceRequest(
        project_id="PAL_EYES",
        request="assess next action",
    )
    result = EngineeringAdvisor().advise(request)
    assert result.status == "RECONCILIATION_REQUIRED"
    assert result.next_safe_action.mutation_ready is False
