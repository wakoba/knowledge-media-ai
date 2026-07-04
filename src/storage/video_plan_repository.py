from datetime import date
from pathlib import Path

from models.atlas import AtlasVideoPlanResult


class VideoPlanRepository:
    """
    Atlasの動画設計結果を保存するRepository。

    保存先:
    output/YYYY-MM-DD/run_HHMMSS/video_plan.json
    output/YYYY-MM-DD/run_HHMMSS/video_plan.md
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
        video_plan: AtlasVideoPlanResult,
        plan_date: date | None = None,
    ) -> dict[str, Path]:
        output_dir = self._resolve_output_dir(plan_date)
        output_dir.mkdir(parents=True, exist_ok=True)

        target_date = plan_date or date.today()

        json_path = self._save_json(video_plan, output_dir)
        md_path = self._save_markdown(video_plan, output_dir, target_date)

        return {
            "json": json_path,
            "markdown": md_path,
        }

    def _resolve_output_dir(
        self,
        plan_date: date | None = None,
    ) -> Path:
        if self.run_dir is not None:
            return self.run_dir

        target_date = plan_date or date.today()
        return self.base_dir / target_date.isoformat()

    def _save_json(
        self,
        video_plan: AtlasVideoPlanResult,
        output_dir: Path,
    ) -> Path:
        json_path = output_dir / "video_plan.json"

        json_path.write_text(
            video_plan.model_dump_json(indent=2),
            encoding="utf-8",
        )

        return json_path

    def _save_markdown(
        self,
        video_plan: AtlasVideoPlanResult,
        output_dir: Path,
        plan_date: date,
    ) -> Path:
        md_path = output_dir / "video_plan.md"

        lines = [
            "# Atlas Video Plan",
            "",
            f"Date: {plan_date.isoformat()}",
            "",
            "## Title",
            "",
            video_plan.title,
            "",
            "## Video Concept",
            "",
            video_plan.video_concept,
            "",
            "## Estimated Duration",
            "",
            f"{video_plan.estimated_duration_minutes} minutes",
            "",
            "## Visual Style",
            "",
            video_plan.visual_style,
            "",
            "## Target Viewer",
            "",
            video_plan.target_viewer,
            "",
            "## Opening Visual",
            "",
            video_plan.opening_visual,
            "",
            "## Scene Plan",
            "",
        ]

        for scene in video_plan.scene_plan:
            lines.extend(
                [
                    f"### Scene {scene.scene_number}: {scene.section_heading}",
                    "",
                    "Narration Summary:",
                    "",
                    scene.narration_summary,
                    "",
                    "Visual Description:",
                    "",
                    scene.visual_description,
                    "",
                    "On-screen Text:",
                    "",
                    scene.on_screen_text,
                    "",
                    "Asset Type:",
                    "",
                    scene.asset_type,
                    "",
                    "Editing Notes:",
                    "",
                    scene.editing_notes,
                    "",
                ]
            )

            if scene.safety_notes:
                lines.extend(
                    [
                        "Safety Notes:",
                        "",
                        scene.safety_notes,
                        "",
                    ]
                )

        lines.extend(
            [
                "## B-roll Ideas",
                "",
            ]
        )

        if video_plan.b_roll_ideas:
            for idea in video_plan.b_roll_ideas:
                lines.append(f"- {idea}")
        else:
            lines.append("- None")

        lines.extend(
            [
                "",
                "## Diagram Ideas",
                "",
            ]
        )

        if video_plan.diagram_ideas:
            for idea in video_plan.diagram_ideas:
                lines.append(f"- {idea}")
        else:
            lines.append("- None")

        lines.extend(
            [
                "",
                "## Subtitle Direction",
                "",
                video_plan.subtitle_direction,
                "",
                "## Narration Direction",
                "",
                video_plan.narration_direction,
                "",
                "## Thumbnail Direction",
                "",
                video_plan.thumbnail_direction,
                "",
                "## Production Notes",
                "",
            ]
        )

        if video_plan.production_notes:
            for note in video_plan.production_notes:
                lines.append(f"- {note}")
        else:
            lines.append("- None")

        lines.append("")

        md_path.write_text(
            "\n".join(lines),
            encoding="utf-8",
        )

        return md_path
