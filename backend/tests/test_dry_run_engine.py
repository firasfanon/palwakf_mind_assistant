from palwakf_mind_assistant.services.dry_run_engine import DryRunEngine


def test_dry_run_never_mutates():
    result=DryRunEngine().preview("P",("edit file",))
    assert result.status.value=="SIMULATED"
    assert result.mutation_executed is False

