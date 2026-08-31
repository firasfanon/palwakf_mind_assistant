from __future__ import annotations

import re

from palwakf_mind_assistant.domain.models import (
    PromptInjectionFinding,
    SecretBoundaryFinding,
)


class SecurityEngine:
    def inspect(
        self,
        text: str,
    ) -> tuple[PromptInjectionFinding, SecretBoundaryFinding]:
        normalized = text.casefold()
        injection_markers = (
            "ignore previous",
            "ignore all instructions",
            "system prompt",
            "bypass authorization",
        )
        injection_detected = any(
            marker in normalized for marker in injection_markers
        )
        secret_detected = bool(
            re.search(
                r"(?i)(password|secret|token|api[_-]?key|service[_-]?role)"
                r"\s*[:=]\s*\S+",
                text,
            )
        )
        return (
            PromptInjectionFinding(
                finding_id="prompt-injection",
                detected=injection_detected,
                severity="HIGH" if injection_detected else "NONE",
                detail=(
                    "High-risk capability must be denied."
                    if injection_detected
                    else "No injection indicator detected."
                ),
            ),
            SecretBoundaryFinding(
                finding_id="secret-boundary",
                detected=secret_detected,
                redacted=secret_detected,
                detail=(
                    "Secret-like value redacted/rejected."
                    if secret_detected
                    else "No secret-like value detected."
                ),
            ),
        )
