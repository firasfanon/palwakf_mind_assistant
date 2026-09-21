from palwakf_mind_assistant.domain.models import (
    ResolutionStatus,
    WatcherDefinition,
    WatcherEvent,
)
from palwakf_mind_assistant.services.authority_resolver import AuthorityResolver


class WatcherService:
    def __init__(self, resolver: AuthorityResolver) -> None:
        self._resolver = resolver

    def definitions(
        self,
        project_id: str,
    ) -> tuple[WatcherDefinition, ...]:
        return (
            WatcherDefinition(
                watcher_id="WATCH-DRIFT",
                project_id=project_id.strip().upper(),
                condition="SOURCE_STALE_OR_DRIFT",
            ),
        )

    def evaluate(
        self,
        project_id: str,
    ) -> tuple[WatcherEvent, ...]:
        normalized = project_id.strip().upper()
        resolution = self._resolver.resolve_project(normalized)
        connector = self._resolver.connector_health()
        needs_reconciliation = (
            resolution.status is not ResolutionStatus.RESOLVED
            or connector.state.value != "READY"
        )
        return (
            WatcherEvent(
                event_id=f"EVENT-DRIFT-{normalized}",
                watcher_id="WATCH-DRIFT",
                state=(
                    "RECONCILE_REQUIRED"
                    if needs_reconciliation
                    else "STABLE_NO_AUTONOMOUS_MUTATION"
                ),
                detail=(
                    f"authority={resolution.status.value}; "
                    f"connector={connector.state.value}; "
                    "watcher may notify/propose only."
                ),
            ),
        )
