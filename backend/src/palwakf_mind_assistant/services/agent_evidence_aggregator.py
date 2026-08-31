from palwakf_mind_assistant.domain.models import MultiAgentPlan


class AgentEvidenceAggregator:
    def aggregate(self, plan: MultiAgentPlan) -> tuple[str,...]:
        return tuple(ref for receipt in plan.receipts for ref in receipt.evidence_refs)

