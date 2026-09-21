from palwakf_mind_assistant.services.repository_analyzer import RepositoryAnalyzer


def _clear_runtime_identity(monkeypatch) -> None:
    for key in (
        "MIND_REPOSITORY_HEAD_SHA",
        "MIND_REPOSITORY_REF",
        "VERCEL_GIT_COMMIT_SHA",
        "VERCEL_GIT_COMMIT_REF",
    ):
        monkeypatch.delenv(key, raising=False)


def test_missing_runtime_identity_fails_closed(monkeypatch):
    _clear_runtime_identity(monkeypatch)
    mind = RepositoryAnalyzer().analyze("PALWAKF_MIND_ASSISTANT")
    eyes = RepositoryAnalyzer().analyze("PAL_EYES")
    assert mind.status == "PARTIAL"
    assert mind.snapshot is not None
    assert mind.snapshot.current_ref.head_sha == "UNKNOWN"
    assert "LIVE_HEAD_REQUIRED_BEFORE_MUTATION" in mind.unknown_reasons
    assert mind.mutation_ready is False
    assert eyes.status == "PARTIAL"


def test_runtime_identity_is_exact_read_only_evidence(monkeypatch):
    _clear_runtime_identity(monkeypatch)
    sha = "32997903cbf9a86e7fea45099da5295ad683d776"
    branch = "task/MIND-L5-ONE-MEGA-BATCH-V1"
    monkeypatch.setenv("MIND_REPOSITORY_HEAD_SHA", sha)
    monkeypatch.setenv("MIND_REPOSITORY_REF", branch)
    mind = RepositoryAnalyzer().analyze("PALWAKF_MIND_ASSISTANT")
    assert mind.status == "RESOLVED"
    assert mind.snapshot is not None
    assert mind.snapshot.current_ref.head_sha == sha
    assert mind.snapshot.current_ref.ref == branch
    assert mind.mutation_ready is False
