from palwakf_mind_assistant.domain.models import ImpactAnalysisRequest
from palwakf_mind_assistant.services.impact_analyzer import ImpactAnalyzer


def test_contract_change_emits_cross_project_review():
    request = ImpactAnalysisRequest(
        project_id="A",
        proposed_change="shared contract change",
        dependencies=("B",),
    )
    result = ImpactAnalyzer().analyze(request)
    assert result.cross_project_impacts
    assert result.overall_severity.value == "REVIEW"
