from palwakf_mind_assistant.services.agent_orchestrator import AgentOrchestrator


def test_agent_plan_has_four_roles_and_no_authority_expansion():
    p=AgentOrchestrator().plan("PALWAKF_MIND_ASSISTANT")
    assert len(p.tasks)==4 and len(p.receipts)==4
    assert p.authority_expanded is False
    assert all(not t.may_expand_authority for t in p.tasks)

