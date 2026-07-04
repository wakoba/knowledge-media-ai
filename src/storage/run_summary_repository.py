from pathlib import Path

from models.athena import AthenaScriptResult
from models.orion import OrionResearchResult
from models.polaris import PolarisResult
from models.sophia import SophiaReviewResult
from storage.run_context import RunContext


class RunSummaryRepository:
    """
    1回の実行結果をまとめた run_summary.md を保存するRepository。

    保存先:
    output/YYYY-MM-DD/run_HHMMSS/run_summary.md
    """

    def __init__(self, run_dir: Path | str):
        self.run_dir = Path(run_dir)
        self.run_dir.mkdir(parents=True, exist_ok=True)

    def save(
        self,
        run_context: RunContext,
        meeting: PolarisResult,
        research: OrionResearchResult,
        script: AthenaScriptResult,
        review: SophiaReviewResult | None = None,
        output_paths: dict[str, dict[str, Path]] | None = None,
    ) -> Path:
        """
        run_summary.md を保存する。
        """

        summary_path = self.run_dir / "run_summary.md"

        choice = meeting.editors_choice
        selected_topic = meeting.topics[choice.index]

        lines = [
            "# Project Polaris Run Summary",
            "",
            f"Run ID: {run_context.run_id}",
            f"Date: {run_context.date_text}",
            f"Run Directory: {run_context.run_dir}",
            "",
            "---",
            "",
            "## Quality Gate",
            "",
        ]

        lines.extend(self._build_quality_gate_lines(review))

        lines.extend(
            [
                "",
                "---",
                "",
                "## Editor's Choice",
                "",
                f"### {selected_topic.title}",
                "",
                "### Reason",
                "",
                choice.reason,
                "",
                "---",
                "",
                "## Topic Candidates",
                "",
            ]
        )

        for i, topic in enumerate(meeting.topics, start=1):
            lines.extend(
                [
                    f"### {i}. {topic.title}",
                    "",
                    f"- Score: {topic.curiosity_score}",
                    f"- Summary: {topic.summary}",
                    f"- Value: {topic.value}",
                    f"- Audience: {topic.audience}",
                    f"- Education: {topic.education}",
                    f"- Reason: {topic.reason}",
                    "",
                ]
            )

        lines.extend(
            [
                "---",
                "",
                "## Orion Research Overview",
                "",
                research.overview,
                "",
                "## Key Facts",
                "",
            ]
        )

        for fact in research.key_facts[:8]:
            lines.append(f"- {fact}")

        lines.extend(
            [
                "",
                "## Why It Matters",
                "",
                research.why_it_matters,
                "",
                "---",
                "",
                "## Athena Script",
                "",
                "### Title",
                "",
                script.title,
                "",
                "### Video Concept",
                "",
                script.video_concept,
                "",
                "### Hook",
                "",
                script.hook,
                "",
                "### Sections",
                "",
            ]
        )

        for section in script.sections:
            lines.append(f"- {section.heading}")

        lines.extend(
            [
                "",
                "### Closing",
                "",
                script.closing,
                "",
            ]
        )

        if review is not None:
            lines.extend(
                [
                    "---",
                    "",
                    "## Sophia Review",
                    "",
                    f"- Approved: {review.approved}",
                    f"- Risk Level: {review.risk_level}",
                    f"- Issue Count: {len(review.issues)}",
                    "",
                    "### Overall Assessment",
                    "",
                    review.overall_assessment,
                    "",
                ]
            )

            if review.issues:
                lines.extend(
                    [
                        "### Issues",
                        "",
                    ]
                )

                for i, issue in enumerate(review.issues, start=1):
                    lines.extend(
                        [
                            f"#### {i}. {issue.type}",
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

        lines.extend(
            [
                "---",
                "",
                "## Output Files",
                "",
            ]
        )

        if output_paths:
            for group_name, paths in output_paths.items():
                lines.append(f"### {group_name}")

                for label, path in paths.items():
                    lines.append(f"- {label}: {path}")

                lines.append("")
        else:
            for path in sorted(self.run_dir.iterdir()):
                if path.is_file():
                    lines.append(f"- {path.name}")

            lines.append("")

        summary_path.write_text(
            "\n".join(lines),
            encoding="utf-8",
        )

        return summary_path

    def _build_quality_gate_lines(
        self,
        review: SophiaReviewResult | None,
    ) -> list[str]:
        """
        Sophiaレビュー結果からQuality Gate表示を作る。
        """

        if review is None:
            return [
                "Status: Not Reviewed",
                "",
                "Sophia review has not been completed for this run.",
            ]

        if review.approved:
            status = "Approved for Publish"
        else:
            status = "Needs Revision"

        lines = [
            f"Status: {status}",
            f"Risk Level: {review.risk_level}",
            f"Sophia Approved: {review.approved}",
            f"Issue Count: {len(review.issues)}",
        ]

        if not review.approved:
            lines.extend(
                [
                    "",
                    "### Required Revisions",
                    "",
                ]
            )

            if review.required_revisions:
                for revision in review.required_revisions:
                    lines.append(f"- {revision}")
            elif review.issues:
                for issue in review.issues:
                    lines.append(f"- {issue.suggested_revision}")
            else:
                lines.append("- Review was not approved, but no specific revision was provided.")

        return lines
