from palwakf_mind_assistant.domain.models import DataClassification


class DataClassifier:
    def classify(self, text: str) -> DataClassification:
        normalized = text.casefold()
        secret_markers = (
            "password",
            "secret",
            "token",
            "api_key",
            "service_role",
        )
        if any(marker in normalized for marker in secret_markers):
            return DataClassification.SECRET
        return DataClassification.INTERNAL
