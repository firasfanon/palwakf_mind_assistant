from __future__ import annotations

from palwakf_mind_assistant.domain.models import (
    AgentRole,
    AgentRunReceipt,
    AgentTask,
    MultiAgentPlan,
)
from palwakf_mind_assistant.services.mega_batch_core import (
    envelope_for,
    stable_id,
)


class AgentOrchestrator:
    def plan(self, project_id: str) -> MultiAgentPlan:
        envelope = envelope_for(project_id)
        tasks = tuple(
            AgentTask(
                agent_task_id=stable_id(
                    "agent",
                    project_id,
                    role.value,
                ),
                role=role,
                objective=f"{role.value} governed development evidence",
                authority_envelope_id=envelope.envelope_id,
                may_expand_authority=False,
            )
            for role in AgentRole
        )
        receipts = tuple(
            AgentRunReceipt(
                agent_task_id=task.agent_task_id,
                role=task.role,
                status="SIMULATED",
                evidence_refs=("FIXTURE_DERIVED",),
            )
            for task in tasks
        )
        return MultiAgentPlan(
            plan_id=stable_id("multi", project_id),
            project_id=project_id,
            tasks=tasks,
            receipts=receipts,
            authority_expanded=False,
        )
