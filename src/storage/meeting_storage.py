from datetime import date
from pathlib import Path

from models.polaris import PolarisResult


class MeetingStorage:
    """
    Polarisの編集会議結果を保存するクラス。
    JSONとMarkdownの両方を output/YYYY-MM-DD/ に保存する。
    """

    def __init__(self, base_dir: str = "output"):
        today = date.today().isoformat()
        self.output_dir = Path(base_dir) / today
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_json(self, meeting: PolarisResult) -> Path:
        json_path = self.output_dir / "meeting.json"

        json_path.write_text(
            meeting.model_dump_json(indent=2),
            encoding="utf-8",
        )

        return json_path

    def save_markdown(self, meeting: PolarisResult) -> Path:
        md_path = self.output_dir / "meeting.md"

        choice = meeting.editors_choice
        selected_topic = meeting.topics[choice.index]

        lines = [
            "# Editorial Meeting",
            "",
            f"Date: {date.today().isoformat()}",
            "",
            "## Topics",
            "",
        ]

        for i, topic in enumerate(meeting.topics):
            lines.extend(
                [
                    f"### {i + 1}. {topic.title}",
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
                "## Editor's Choice",
                "",
                f"### {selected_topic.title}",
                "",
                f"Choice Index: {choice.index}",
                "",
                "### Reason",
                "",
                choice.reason,
                "",
            ]
        )

        md_path.write_text(
            "\n".join(lines),
            encoding="utf-8",
        )

        return md_path

    def save(self, meeting: PolarisResult) -> dict[str, Path]:
        json_path = self.save_json(meeting)
        md_path = self.save_markdown(meeting)

        return {
            "json": json_path,
            "markdown": md_path,
        }
