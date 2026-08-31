from __future__ import annotations

from palwakf_mind_assistant.domain.models import (
    PlanningEdge,
    PlanningGraph,
    PlanningNode,
    PlanningRequest,
    PlanningResponse,
    PlanNodeType,
    PlanStatus,
)
from palwakf_mind_assistant.services.mega_batch_core import stable_id


class PlanningEngine:
    def plan(
        self,
        request: PlanningRequest,
        *,
        source_refs: tuple[str, ...] = (),
        skill_ids: tuple[str, ...] = (),
    ) -> PlanningResponse:
        project_id = request.project_id.upper()
        nodes = (
            PlanningNode(
                node_id="context",
                node_type=PlanNodeType.CONTEXT,
                title="Restore trusted context",
                status="READY",
                source_refs=source_refs,
            ),
            PlanningNode(
                node_id="plan",
                node_type=PlanNodeType.ACTION,
                title=request.goal,
                status="PROPOSED",
                source_refs=source_refs,
            ),
            PlanningNode(
                node_id="review",
                node_type=PlanNodeType.DECISION,
                title="Human review",
                status="REQUIRED",
                requires_approval=True,
            ),
            PlanningNode(
                node_id="verify",
                node_type=PlanNodeType.VERIFICATION,
                title="Independent verification",
                status="REQUIRED",
            ),
            PlanningNode(
                node_id="checkpoint",
                node_type=PlanNodeType.CHECKPOINT,
                title="Knowledge/state checkpoint",
                status="PENDING",
            ),
        )
        edges = tuple(
            PlanningEdge(
                from_node=current.node_id,
                to_node=following.node_id,
                relation="PRECEDES",
            )
            for current, following in zip(nodes, nodes[1:], strict=False)
        )
        graph = PlanningGraph(
            plan_id=stable_id("plan", project_id, request.goal),
            project_id=project_id,
            status=PlanStatus.REVIEW_REQUIRED,
            nodes=nodes,
            edges=edges,
            risks=("UNKNOWN_REMAINS_UNKNOWN",),
            source_refs=source_refs,
        )
        return PlanningResponse(
            graph=graph,
            applicable_skill_ids=skill_ids,
            approval_required=True,
        )
