from palwakf_mind_assistant.adapters.drive_readonly import InMemoryDriveReadOnlyAdapter
from palwakf_mind_assistant.domain.models import (
    AuthorityType,
    LifecycleStatus,
    ResolutionStatus,
    SourceRef,
)
from palwakf_mind_assistant.services.authority_resolver import AuthorityResolver


def _source(
    *,
    source_id: str,
    authority_type: AuthorityType,
    lifecycle_status: LifecycleStatus,
) -> SourceRef:
    return SourceRef(
        owner_project_id="PAL_EYES",
        authority_type=authority_type,
        lifecycle_status=lifecycle_status,
        canonical_location=f"gdrive://{source_id}",
        source_id=source_id,
        source_ref=f"drive:{source_id}",
        title=source_id,
    )


def test_pal_eyes_resolves_deterministically_and_preserves_provenance() -> None:
    sources = (
        _source(
            source_id="current-state",
            authority_type=AuthorityType.PROJECT_CURRENT_STATE,
            lifecycle_status=LifecycleStatus.CURRENT,
        ),
        _source(
            source_id="portfolio-registry",
            authority_type=AuthorityType.PORTFOLIO_REGISTRY,
            lifecycle_status=LifecycleStatus.ACTIVE,
        ),
        _source(
            source_id="old-current-state",
            authority_type=AuthorityType.PROJECT_CURRENT_STATE,
            lifecycle_status=LifecycleStatus.SUPERSEDED,
        ),
    )

    resolution = AuthorityResolver(InMemoryDriveReadOnlyAdapter(sources)).resolve_project(
        "pal_eyes"
    )

    assert resolution.status is ResolutionStatus.RESOLVED
    assert resolution.project_id == "PAL_EYES"
    assert [item.source_id for item in resolution.authoritative_sources] == [
        "current-state",
        "portfolio-registry",
    ]
    assert [item.source_id for item in resolution.superseded_sources] == ["old-current-state"]
    assert all(item.source_ref.startswith("drive:") for item in resolution.authoritative_sources)


def test_all_authority_types_have_priority_and_do_not_key_error() -> None:
    sources = tuple(
        _source(
            source_id=authority.value,
            authority_type=authority,
            lifecycle_status=LifecycleStatus.ACTIVE,
        )
        for authority in AuthorityType
        if authority is not AuthorityType.UNKNOWN
    )
    resolution = AuthorityResolver(InMemoryDriveReadOnlyAdapter(sources)).resolve_project(
        "PAL_EYES"
    )
    assert resolution.status is ResolutionStatus.RESOLVED
    assert len(resolution.authoritative_sources) == len(sources)


def test_multiple_current_sources_are_partial_not_silently_resolved() -> None:
    sources = (
        _source(
            source_id="current-a",
            authority_type=AuthorityType.PROJECT_CURRENT_STATE,
            lifecycle_status=LifecycleStatus.CURRENT,
        ),
        _source(
            source_id="current-b",
            authority_type=AuthorityType.PROJECT_CURRENT_STATE,
            lifecycle_status=LifecycleStatus.CURRENT,
        ),
    )
    resolution = AuthorityResolver(InMemoryDriveReadOnlyAdapter(sources)).resolve_project(
        "PAL_EYES"
    )
    assert resolution.status is ResolutionStatus.PARTIAL
    assert "MULTIPLE_CURRENT:PROJECT_CURRENT_STATE" in resolution.unknown_reasons


def test_unknown_project_fails_closed() -> None:
    resolution = AuthorityResolver(InMemoryDriveReadOnlyAdapter(())).resolve_project("UNKNOWN_X")
    assert resolution.status is ResolutionStatus.UNKNOWN
    assert resolution.authoritative_sources == ()
    assert resolution.unknown_reasons == ("NO_AUTHORITATIVE_SOURCE_FOUND",)


def test_unknown_lifecycle_is_not_promoted_to_current() -> None:
    source = _source(
        source_id="ambiguous",
        authority_type=AuthorityType.PROJECT_CURRENT_STATE,
        lifecycle_status=LifecycleStatus.UNKNOWN,
    )
    resolution = AuthorityResolver(InMemoryDriveReadOnlyAdapter((source,))).resolve_project(
        "PAL_EYES"
    )
    assert resolution.status is ResolutionStatus.UNKNOWN
    assert resolution.authoritative_sources == ()
    assert "UNKNOWN_LIFECYCLE:PROJECT_CURRENT_STATE" in resolution.unknown_reasons
