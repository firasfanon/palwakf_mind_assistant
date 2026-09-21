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
            "disregard previous",
            "override system",
            "system prompt",
            "developer message",
            "reveal system",
            "bypass authorization",
            "disable safety",
            "تجاهل التعليمات",
            "تجاوز الصلاحيات",
        )
        injection_detected = any(
            marker in normalized for marker in injection_markers
        )
        secret_detected = bool(
            re.search(
                r"(?i)(?:"
                r"(?:password|secret|token|api[_-]?key|service[_-]?role"
                r"|github[_-]?token|private[_-]?key)\s*[:=]\s*\S{6,}"
                r"|authorization\s*:\s*bearer\s*\S{6,}"
                r"|bearer\s+\S{6,}"
                r")",
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
