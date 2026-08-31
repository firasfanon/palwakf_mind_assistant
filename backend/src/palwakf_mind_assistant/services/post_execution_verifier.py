from palwakf_mind_assistant.domain.models import ExecutionReceipt


class PostExecutionVerifier:
    def verify(self, receipt: ExecutionReceipt) -> bool:
        return receipt.simulated and not receipt.mutation_executed

