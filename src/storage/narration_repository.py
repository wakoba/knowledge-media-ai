from datetime import date
from pathlib import Path

from models.narrator import NarrationScriptResult


class NarrationRepository:
    """
    Narratorのナレーション原稿を保存するRepository。

    保存先:
    output/YYYY-MM-DD/run_HHMMSS/narration_script.json
    output/YYYY-MM-DD/run_HHMMSS/narration_script.md
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
        narration: NarrationScriptResult,
        narration_date: date | None = None,
    ) -> dict[str, Path]:
        output_dir = self._resolve_output_dir(narration_date)
        output_dir.mkdir(parents=True, exist_ok=True)

        target_date = narration_date or date.today()

        json_path = self._save_json(narration, output_dir)
        md_path = self._save_markdown(narration, output_dir, target_date)

        return {
            "json": json_path,
            "markdown": md_path,
        }

    def _resolve_output_dir(
        self,
        narration_date: date | None = None,
    ) -> Path:
        if self.run_dir is not None:
            return self.run_dir

        target_date = narration_date or date.today()
        return self.base_dir / target_date.isoformat()

    def _save_json(
        self,
        narration: NarrationScriptResult,
        output_dir: Path,
    ) -> Path:
        json_path = output_dir / "narration_script.json"

        json_path.write_text(
            narration.model_dump_json(indent=2),
            encoding="utf-8",
        )

        return json_path

    def _save_markdown(
        self,
        narration: NarrationScriptResult,
        output_dir: Path,
        narration_date: date,
    ) -> Path:
        md_path = output_dir / "narration_script.md"

        lines = [
            "# Narration Script",
            "",
            f"Date: {narration_date.isoformat()}",
            "",
            "## Title",
            "",
            narration.title,
            "",
            "## Narration Style",
            "",
            narration.narration_style,
            "",
            "## Estimated Duration",
            "",
            f"{narration.estimated_duration_minutes} minutes",
            "",
            "## Opening Line",
            "",
            narration.opening_line,
            "",
            "## Segments",
            "",
        ]

        for segment in narration.segments:
            lines.extend(
                [
                    f"### Scene {segment.scene_number}: {segment.section_heading}",
                    "",
                    "Narration:",
                    "",
                    segment.narration_text,
                    "",
                    "Subtitle Text:",
                    "",
                    segment.subtitle_text,
                    "",
                    "Pacing Notes:",
                    "",
                    segment.pacing_notes,
                    "",
                    "Voice Notes:",
                    "",
                    segment.voice_notes,
                    "",
                    "Visual Sync Notes:",
                    "",
                    segment.visual_sync_notes,
                    "",
                ]
            )

        lines.extend(
            [
                "## Closing Line",
                "",
                narration.closing_line,
                "",
                "## Pronunciation Notes",
                "",
            ]
        )

        if narration.pronunciation_notes:
            for note in narration.pronunciation_notes:
                lines.append(f"- {note}")
        else:
            lines.append("- None")

        lines.extend(
            [
                "",
                "## Subtitle Notes",
                "",
                narration.subtitle_notes,
                "",
                "## Audio Production Notes",
                "",
            ]
        )

        if narration.audio_production_notes:
            for note in narration.audio_production_notes:
                lines.append(f"- {note}")
        else:
            lines.append("- None")

        lines.append("")

        md_path.write_text(
            "\n".join(lines),
            encoding="utf-8",
        )

        return md_path
