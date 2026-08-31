from palwakf_mind_assistant.services.repository_analyzer import RepositoryAnalyzer


def test_two_repository_profiles_preserve_exact_or_unknown_refs():
    mind=RepositoryAnalyzer().analyze("PALWAKF_MIND_ASSISTANT")
    eyes=RepositoryAnalyzer().analyze("PAL_EYES")
    assert mind.snapshot.current_ref.head_sha=="8fc746291043a9de9b0b19c477a2d32ae1a06e8a"
    assert mind.mutation_ready is False
    assert eyes.status=="PARTIAL"
    assert "LIVE_HEAD_REQUIRED_BEFORE_MUTATION" in eyes.unknown_reasons

