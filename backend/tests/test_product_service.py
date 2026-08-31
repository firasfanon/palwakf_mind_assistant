from palwakf_mind_assistant.adapters.drive_readonly import InMemoryDriveReadOnlyAdapter
from palwakf_mind_assistant.domain.models import (
    AssistantQuestion,
    AuthorityType,
    LifecycleStatus,
    ResolutionStatus,
    SourceRef,
)
from palwakf_mind_assistant.services.authority_resolver import AuthorityResolver
from palwakf_mind_assistant.services.product_service import ProductService


def _source(
    source_id: str,
    *,
    authority: AuthorityType,
    lifecycle: LifecycleStatus,
    title: str,
) -> SourceRef:
    return SourceRef(
        owner_project_id="PAL_EYES",
        authority_type=authority,
        lifecycle_status=lifecycle,
        canonical_location=f"drive://{source_id}",
        source_id=source_id,
        source_ref=f"drive:{source_id}",
        title=title,
    )


def _service() -> ProductService:
    sources = (
        _source(
            "current",
            authority=AuthorityType.PROJECT_CURRENT_STATE,
            lifecycle=LifecycleStatus.CURRENT,
            title="PAL_EYES_CURRENT_STATE",
        ),
        _source(
            "registry",
            authority=AuthorityType.PORTFOLIO_REGISTRY,
            lifecycle=LifecycleStatus.ACTIVE,
            title="PORTFOLIO_REGISTRY",
        ),
    )
    return ProductService(AuthorityResolver(InMemoryDriveReadOnlyAdapter(sources)))


def test_dashboard_project_mind_and_assistant_share_authority_core() -> None:
    service = _service()
    dashboard = service.dashboard()
    mind = service.project_mind("PAL_EYES")
    answer = service.ask(AssistantQuestion(message="ما آخر حالة لمشروع Pal Eyes؟"))

    assert dashboard.projects[0].authority_status is ResolutionStatus.RESOLVED
    assert dashboard.projects[0].current_state_title == "PAL_EYES_CURRENT_STATE"
    assert dashboard.projects[0].knowledge_health == "HEALTHY"
    assert mind.current_state is not None
    assert mind.current_state.title == "PAL_EYES_CURRENT_STATE"
    assert answer.project_id == "PAL_EYES"
    assert answer.status == "GROUNDED_READ_ONLY"
    assert answer.citations[0].title == "PAL_EYES_CURRENT_STATE"


def test_assistant_fails_closed_without_project_context() -> None:
    answer = _service().ask(AssistantQuestion(message="ما آخر حالة؟"))
    assert answer.status == "NEEDS_PROJECT_CONTEXT"
    assert answer.confidence == "UNKNOWN"
    assert answer.unknown_reasons == ("PROJECT_CONTEXT_NOT_DETERMINISTIC",)


def test_knowledge_search_is_metadata_grounded() -> None:
    result = _service().search("CURRENT_STATE", "PAL_EYES")
    assert result.total == 1
    assert result.hits[0].source_ref == "drive:current"
    assert "title" in result.hits[0].matched_on


def test_assistant_does_not_silently_choose_between_multiple_current_sources() -> None:
    sources = (
        _source(
            "a",
            authority=AuthorityType.PROJECT_CURRENT_STATE,
            lifecycle=LifecycleStatus.CURRENT,
            title="CURRENT_A",
        ),
        _source(
            "b",
            authority=AuthorityType.PROJECT_CURRENT_STATE,
            lifecycle=LifecycleStatus.CURRENT,
            title="CURRENT_B",
        ),
    )
    service = ProductService(AuthorityResolver(InMemoryDriveReadOnlyAdapter(sources)))
    answer = service.ask(AssistantQuestion(message="ما الحالة الحالية لمشروع Pal Eyes؟"))
    assert answer.status == "CONFLICT_REVIEW_REQUIRED"
    assert answer.confidence == "REVIEW_REQUIRED"
    assert "MULTIPLE_CURRENT_SOURCES" in answer.unknown_reasons
