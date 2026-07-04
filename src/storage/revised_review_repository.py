from datetime import date
from pathlib import Path

from models.sophia import SophiaReviewResult


class RevisedReviewRepository:
    """
    Sophiaの再レビュー結果を保存するRepository。

    保存先:
    output/YYYY-MM-DD/run_HHMMSS/revised_review.json
    output/YYYY-MM-DD/run_HHMMSS/revised_review.md
    """

    def __init__(
        self,
        base_dir: str = "output",
        run_dir: Path | str | None = None,
    ):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

        self.run_dir = Path(run_dir) if run_dir is not None else None

    def save(
        self,
        review: SophiaReviewResult,
        review_date: date | None = None,
    ) -> dict[str, Path]:
        output_dir = self._resolve_output_dir(review_date)
        output_dir.mkdir(parents=True, exist_ok=True)

        target_date = review_date or date.today()

        json_path = self._save_json(review, output_dir)
        md_path = self._save_markdown(review, output_dir, target_date)

        return {
            "json": json_path,
            "markdown": md_path,
        }

    def _resolve_output_dir(
        self,
        review_date: date | None = None,
    ) -> Path:
        if self.run_dir is not None:
            return self.run_dir

        target_date = review_date or date.today()

        return self.base_dir / target_date.isoformat()

    def _save_json(
        self,
        review: SophiaReviewResult,
        output_dir: Path,
    ) -> Path:
        json_path = output_dir / "revised_review.json"

        json_path.write_text(
            review.model_dump_json(indent=2),
            encoding="utf-8",
        )

        return json_path

    def _save_markdown(
        self,
        review: SophiaReviewResult,
        output_dir: Path,
        review_date: date,
    ) -> Path:
        md_path = output_dir / "revised_review.md"

        lines = [
            "# Sophia Revised Review",
            "",
            f"Date: {review_date.isoformat()}",
            "",
            "## Approval",
            "",
            f"Approved: {review.approved}",
            "",
            "## Risk Level",
            "",
            review.risk_level,
            "",
            "## Overall Assessment",
            "",
            review.overall_assessment,
            "",
            "## Issues",
            "",
        ]

        if review.issues:
            for i, issue in enumerate(review.issues, start=1):
                lines.extend(
                    [
                        f"### {i}. {issue.type}",
                        "",
                        f"- Severity: {issue.severity}",
                        f"- Original Text: {issue.original_text}",
                        "",
                        "Problem:",
                        "",
                        issue.problem,
                        "",
                        "Suggested Revision:",
                        "",
                        issue.suggested_revision,
                        "",
                    ]
                )
        else:
            lines.append("- No major issues found.")
            lines.append("")

        lines.extend(
            [
                "## Required Revisions",
                "",
            ]
        )

        if review.required_revisions:
            for item in review.required_revisions:
                lines.append(f"- {item}")
        else:
            lines.append("- None")

        lines.extend(
            [
                "",
                "## Optional Improvements",
                "",
            ]
        )

        if review.optional_improvements:
            for item in review.optional_improvements:
                lines.append(f"- {item}")
        else:
            lines.append("- None")

        lines.extend(
            [
                "",
                "## Final Notes",
                "",
                review.final_notes,
                "",
            ]
        )

        md_path.write_text(
            "\n".join(lines),
            encoding="utf-8",
        )

        return md_path
