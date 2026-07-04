from datetime import date
from pathlib import Path

from models.athena import AthenaScriptResult


class RevisedScriptRepository:
    """
    Athenaの修正版台本を保存するRepository。

    保存先:
    output/YYYY-MM-DD/run_HHMMSS/revised_script.json
    output/YYYY-MM-DD/run_HHMMSS/revised_script.md
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
        script: AthenaScriptResult,
        script_date: date | None = None,
    ) -> dict[str, Path]:
        output_dir = self._resolve_output_dir(script_date)
        output_dir.mkdir(parents=True, exist_ok=True)

        target_date = script_date or date.today()

        json_path = self._save_json(script, output_dir)
        md_path = self._save_markdown(script, output_dir, target_date)

        return {
            "json": json_path,
            "markdown": md_path,
        }

    def _resolve_output_dir(
        self,
        script_date: date | None = None,
    ) -> Path:
        if self.run_dir is not None:
            return self.run_dir

        target_date = script_date or date.today()

        return self.base_dir / target_date.isoformat()

    def _save_json(
        self,
        script: AthenaScriptResult,
        output_dir: Path,
    ) -> Path:
        json_path = output_dir / "revised_script.json"

        json_path.write_text(
            script.model_dump_json(indent=2),
            encoding="utf-8",
        )

        return json_path

    def _save_markdown(
        self,
        script: AthenaScriptResult,
        output_dir: Path,
        script_date: date,
    ) -> Path:
        md_path = output_dir / "revised_script.md"

        lines = [
            "# Athena Revised Script",
            "",
            f"Date: {script_date.isoformat()}",
            "",
            "## Title",
            "",
            script.title,
            "",
            "## Video Concept",
            "",
            script.video_concept,
            "",
            "## Target Viewer",
            "",
            script.target_viewer,
            "",
            "## Estimated Duration",
            "",
            f"{script.estimated_duration_minutes} minutes",
            "",
            "## Hook",
            "",
            script.hook,
            "",
            "## Intro",
            "",
            script.intro,
            "",
            "## Sections",
            "",
        ]

        for i, section in enumerate(script.sections, start=1):
            lines.extend(
                [
                    f"### {i}. {section.heading}",
                    "",
                    section.script,
                    "",
                    "Visual Ideas:",
                    "",
                ]
            )

            for visual in section.visual_ideas:
                lines.append(f"- {visual}")

            lines.append("")

        lines.extend(
            [
                "## Closing",
                "",
                script.closing,
                "",
                "## Thumbnail Ideas",
                "",
            ]
        )

        for idea in script.thumbnail_ideas:
            lines.append(f"- {idea}")

        lines.extend(
            [
                "",
                "## Title Ideas",
                "",
            ]
        )

        for idea in script.title_ideas:
            lines.append(f"- {idea}")

        lines.extend(
            [
                "",
                "## Short Summary",
                "",
                script.short_summary,
                "",
                "## Accuracy Notes",
                "",
            ]
        )

        for note in script.accuracy_notes:
            lines.append(f"- {note}")

        lines.append("")

        md_path.write_text(
            "\n".join(lines),
            encoding="utf-8",
        )

        return md_path
