from datetime import date
from pathlib import Path

from models.orion import OrionResearchResult


class ResearchRepository:
    """
    Orionのリサーチ結果を保存するRepository。

    保存先:
    output/YYYY-MM-DD/run_HHMMSS/research.json
    output/YYYY-MM-DD/run_HHMMSS/research.md
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
        research: OrionResearchResult,
        research_date: date | None = None,
    ) -> dict[str, Path]:
        """
        リサーチ結果をJSONとMarkdownで保存する。
        """

        output_dir = self._resolve_output_dir(research_date)
        output_dir.mkdir(parents=True, exist_ok=True)

        target_date = research_date or date.today()

        json_path = self._save_json(research, output_dir)
        md_path = self._save_markdown(research, output_dir, target_date)

        return {
            "json": json_path,
            "markdown": md_path,
        }

    def _resolve_output_dir(
        self,
        research_date: date | None = None,
    ) -> Path:
        if self.run_dir is not None:
            return self.run_dir

        target_date = research_date or date.today()

        return self.base_dir / target_date.isoformat()

    def _save_json(
        self,
        research: OrionResearchResult,
        output_dir: Path,
    ) -> Path:
        json_path = output_dir / "research.json"

        json_path.write_text(
            research.model_dump_json(indent=2),
            encoding="utf-8",
        )

        return json_path

    def _save_markdown(
        self,
        research: OrionResearchResult,
        output_dir: Path,
        research_date: date,
    ) -> Path:
        md_path = output_dir / "research.md"

        lines = [
            "# Orion Research Report",
            "",
            f"Date: {research_date.isoformat()}",
            "",
            "## Topic",
            "",
            research.topic_title,
            "",
            "## Overview",
            "",
            research.overview,
            "",
            "## Key Facts",
            "",
        ]

        for fact in research.key_facts:
            lines.append(f"- {fact}")

        lines.extend(
            [
                "",
                "## Mechanism",
                "",
                research.mechanism,
                "",
                "## Why It Matters",
                "",
                research.why_it_matters,
                "",
                "## Common Misunderstandings",
                "",
            ]
        )

        for item in research.common_misunderstandings:
            lines.append(f"- {item}")

        lines.extend(
            [
                "",
                "## Examples",
                "",
            ]
        )

        for example in research.examples:
            lines.append(f"- {example}")

        lines.extend(
            [
                "",
                "## Story Angles",
                "",
            ]
        )

        for angle in research.story_angles:
            lines.append(f"- {angle}")

        lines.extend(
            [
                "",
                "## Viewer Takeaways",
                "",
            ]
        )

        for takeaway in research.viewer_takeaways:
            lines.append(f"- {takeaway}")

        lines.extend(
            [
                "",
                "## Open Question",
                "",
                research.open_question,
                "",
                "## Research Notes",
                "",
                research.research_notes,
                "",
            ]
        )

        md_path.write_text(
            "\n".join(lines),
            encoding="utf-8",
        )

        return md_path
