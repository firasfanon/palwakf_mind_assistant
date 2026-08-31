from datetime import UTC, datetime

from palwakf_mind_assistant.adapters.drive_readonly import InMemoryDriveReadOnlyAdapter
from palwakf_mind_assistant.domain.models import (
    AuthorityType,
    ClaimState,
    ContextRequest,
    FreshnessState,
    LifecycleStatus,
    SourceRef,
)
from palwakf_mind_assistant.services.authority_resolver import AuthorityResolver
from palwakf_mind_assistant.services.context_compiler import ContextCompiler


def _source(source_id: str, lifecycle: LifecycleStatus) -> SourceRef:
    return SourceRef(
        owner_project_id="PAL_EYES",
        authority_type=AuthorityType.PROJECT_CURRENT_STATE,
        lifecycle_status=lifecycle,
        canonical_location=f"drive://{source_id}",
        source_id=source_id,
        source_ref=f"drive:{source_id}",
        title=f"STATE_{source_id}",
        metadata={"observed_at": datetime(2026, 8, 29, tzinfo=UTC).isoformat()},
    )


def test_compile_requires_deterministic_project_context() -> None:
    compiler = ContextCompiler(AuthorityResolver(InMemoryDriveReadOnlyAdapter(())))
    package = compiler.compile(ContextRequest(message="ما الحالة الحالية؟"))

    assert package.project_id is None
    assert package.trust_state is ClaimState.UNKNOWN
    assert package.unknown_reasons == ("PROJECT_CONTEXT_NOT_DETERMINISTIC",)
    assert package.mutation_mode == "READ_ONLY"


def test_compile_current_authority_is_verified_with_provenance() -> None:
    compiler = ContextCompiler(
        AuthorityResolver(
            InMemoryDriveReadOnlyAdapter((_source("current", LifecycleStatus.CURRENT),))
        )
    )
    package = compiler.compile(ContextRequest(message="ما الحالة الحالية؟", project_id="PAL_EYES"))

    assert package.project_id == "PAL_EYES"
    assert package.trust_state is ClaimState.VERIFIED
    assert len(package.authoritative_sources) == 1
    provenance = package.authoritative_sources[0].provenance
    assert provenance.claim_state is ClaimState.VERIFIED
    assert provenance.freshness is FreshnessState.CURRENT
    assert provenance.source_ref == "drive:current"


def test_compile_multiple_current_sources_fails_closed_as_conflicted() -> None:
    sources = (
        _source("a", LifecycleStatus.CURRENT),
        _source("b", LifecycleStatus.CURRENT),
    )
    compiler = ContextCompiler(AuthorityResolver(InMemoryDriveReadOnlyAdapter(sources)))
    package = compiler.compile(ContextRequest(message="ما الحالة الحالية؟", project_id="PAL_EYES"))

    assert package.trust_state is ClaimState.CONFLICTED
    assert "MULTIPLE_CURRENT_SOURCES" in package.unknown_reasons
    assert "BLOCKING_AUTHORITY_CONFLICT" in package.risks


def test_superseded_source_is_never_promoted_to_verified_current_fact() -> None:
    sources = (
        _source("current", LifecycleStatus.CURRENT),
        _source("old", LifecycleStatus.SUPERSEDED),
    )
    compiler = ContextCompiler(AuthorityResolver(InMemoryDriveReadOnlyAdapter(sources)))
    package = compiler.compile(ContextRequest(message="ما المصادر؟", project_id="PAL_EYES"))

    assert package.trust_state is ClaimState.VERIFIED
    assert len(package.superseded_sources) == 1
    old = package.superseded_sources[0].provenance
    assert old.claim_state is ClaimState.STALE
    assert old.freshness is FreshnessState.STALE


def test_context_compiler_can_include_applicable_skills_without_execution_authority() -> None:
    from datetime import UTC, datetime

    from palwakf_mind_assistant.domain.models import SkillLevel, SkillObject, SkillStatus
    from palwakf_mind_assistant.services.skill_resolver import SkillResolver

    resolver = AuthorityResolver(
        InMemoryDriveReadOnlyAdapter((_source("current", LifecycleStatus.CURRENT),))
    )
    skill = SkillObject(
        skill_id='FLUTTER_UAT',
        version='1.0.0',
        status=SkillStatus.ACTIVE,
        owner_scope='DOMAIN:FLUTTER',
        level=SkillLevel.DOMAIN,
        applies_to=('flutter',),
        triggers=('flutter', 'browser', 'uat'),
        preconditions=(),
        required_inputs=(),
        authorized_operations=('ADVISE',),
        forbidden_operations=('MUTATE',),
        execution_steps=(),
        fail_closed_conditions=(),
        expected_outputs=(),
        evidence_requirements=(),
        regression_tests=(),
        known_failures=(),
        supersedes=(),
        last_validated_at=datetime(2026, 8, 29, tzinfo=UTC),
        provenance_ref='drive:skills#flutter',
    )
    compiler = ContextCompiler(resolver, skill_resolver=SkillResolver((skill,)))
    result = compiler.compile(
        ContextRequest(message='Flutter browser UAT', project_id='PAL_EYES')
    )
    assert result.applicable_skills[0].skill_id == 'FLUTTER_UAT'
    assert result.applicable_skills[0].execution_authorized is False
