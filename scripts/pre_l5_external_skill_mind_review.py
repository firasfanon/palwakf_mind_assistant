from __future__ import annotations

import argparse
import json
from pathlib import Path

from palwakf_mind_assistant.external_skill_review import (
    ExternalSkillReviewRequest,
    review_external_skill,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agentic-evidence", required=True)
    parser.add_argument("--skill-catalog", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    evidence = json.loads(Path(args.agentic_evidence).read_text(encoding="utf-8"))
    catalog = json.loads(Path(args.skill_catalog).read_text(encoding="utf-8"))
    existing_ids = {item["skill_id"] for item in catalog.get("skills", [])}
    reviews: list[dict[str, object]] = []

    for item in evidence["candidates"]:
        sandbox = item["sandbox"]
        parsed_name = item["parsed_name"]
        exact_overlap = tuple(
            skill_id
            for skill_id in existing_ids
            if skill_id.lower() == parsed_name.lower()
        )
        request = ExternalSkillReviewRequest(
            skill_id=parsed_name,
            repository=item["repository"],
            commit_sha=item["commit_sha"],
            path=item["path"],
            license=item["license"],
            provenance_verified=bool(item["source_hash_pass"]),
            source_hash_verified=bool(item["source_hash_pass"]),
            security_findings=tuple(item["security_findings"]),
            overlapping_skill_ids=exact_overlap,
            sensitive_capability_flags=tuple(item.get("capability_flags", ())),
            eval_passed=bool(sandbox["parser_pass"] and sandbox["security_pass"]),
            regression_passed=bool(
                sandbox["source_hash_pass"] and sandbox["authority_pass"]
            ),
            requested_execution_authority=False,
        )
        result = review_external_skill(request)
        reviews.append({**item, "mind_review": result.model_dump(mode="json")})

    summary: dict[str, int] = {}
    for item in reviews:
        decision = item["mind_review"]["decision"]
        summary[decision] = summary.get(decision, 0) + 1

    output = {
        "schema": "PALWAKF_EXTERNAL_SKILL_MIND_REVIEW_V1",
        "candidate_count": len(reviews),
        "canonical_write_allowed": False,
        "auto_promotion": False,
        "execution_authority_granted": False,
        "decision_counts": summary,
        "reviews": reviews,
    }
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps({"candidate_count": len(reviews), "decision_counts": summary}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
