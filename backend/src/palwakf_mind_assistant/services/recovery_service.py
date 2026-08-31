from palwakf_mind_assistant.domain.models import RecoveryReceipt


class RecoveryService:
    def drill(self) -> RecoveryReceipt:
        return RecoveryReceipt(
            recovery_id="RECOVERY-1",
            status="PASS_SIMULATED",
            rebuildable=True,
            canonical_data_loss=False,
            detail=(
                "Derived-store rebuild simulation; canonical Drive "
                "remains the owner."
            ),
        )
