from pathlib import Path

from models.athena import AthenaScriptResult
from models.orion import OrionResearchResult
from models.polaris import PolarisResult
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
                f"### Title",
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
