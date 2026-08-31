from palwakf_mind_assistant.domain.models import (
    WatcherDefinition,
    WatcherEvent,
)


class WatcherService:
    def definitions(
        self,
        project_id: str,
    ) -> tuple[WatcherDefinition, ...]:
        return (
            WatcherDefinition(
                watcher_id="WATCH-DRIFT",
                project_id=project_id,
                condition="SOURCE_STALE_OR_DRIFT",
            ),
        )

    def evaluate(
        self,
        project_id: str,
    ) -> tuple[WatcherEvent, ...]:
        _ = project_id
        return (
            WatcherEvent(
                event_id="EVENT-DRIFT",
                watcher_id="WATCH-DRIFT",
                state="NO_AUTONOMOUS_MUTATION",
                detail="Watcher may notify/propose only.",
            ),
        )
