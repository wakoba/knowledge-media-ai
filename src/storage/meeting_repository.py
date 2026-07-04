from datetime import date
from pathlib import Path
from typing import Optional

from models.polaris import PolarisResult


class MeetingRepository:
    """
    Project Polarisの編集会議データを管理するRepository。

    主な責務:
    - 編集会議結果を保存する
    - 日付指定で編集会議を読み込む
    - 保存済みの日付一覧を取得する
    - 最新の編集会議を読み込む
    """

    def __init__(self, base_dir: str = "output"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(
        self,
        meeting: PolarisResult,
        meeting_date: Optional[date] = None,
    ) -> dict[str, Path]:
        """
        編集会議結果をJSONとMarkdownで保存する。

        保存先:
        output/YYYY-MM-DD/meeting.json
        output/YYYY-MM-DD/meeting.md
        """

        target_date = meeting_date or date.today()
        output_dir = self.base_dir / target_date.isoformat()
        output_dir.mkdir(parents=True, exist_ok=True)

        json_path = self._save_json(meeting, output_dir)
        md_path = self._save_markdown(meeting, output_dir, target_date)

        return {
            "json": json_path,
            "markdown": md_path,
        }

    def load_by_date(self, meeting_date: str) -> PolarisResult:
        """
        指定した日付の編集会議結果を読み込む。

        例:
        repository.load_by_date("2026-07-04")
        """

        json_path = self.base_dir / meeting_date / "meeting.json"

        if not json_path.exists():
            raise FileNotFoundError(
                f"編集会議データが見つかりません: {json_path}"
            )

        json_text = json_path.read_text(encoding="utf-8")

        return PolarisResult.model_validate_json(json_text)

    def list_dates(self) -> list[str]:
        """
        保存済みの編集会議日付一覧を返す。

        例:
        [
            "2026-07-01",
            "2026-07-02",
            "2026-07-04"
        ]
        """

        dates = []

        for path in self.base_dir.iterdir():
            if path.is_dir() and (path / "meeting.json").exists():
                dates.append(path.name)

        return sorted(dates)

    def load_latest(self) -> PolarisResult:
        """
        最新の編集会議結果を読み込む。
        """

        dates = self.list_dates()

        if not dates:
            raise FileNotFoundError(
                "保存済みの編集会議データがありません。"
            )

        latest_date = dates[-1]

        return self.load_by_date(latest_date)

    def _save_json(
        self,
        meeting: PolarisResult,
        output_dir: Path,
    ) -> Path:
        """
        編集会議結果をJSONで保存する。
        """

        json_path = output_dir / "meeting.json"

        json_path.write_text(
            meeting.model_dump_json(indent=2),
            encoding="utf-8",
        )

        return json_path

    def _save_markdown(
        self,
        meeting: PolarisResult,
        output_dir: Path,
        meeting_date: date,
    ) -> Path:
        """
        編集会議結果をMarkdownで保存する。
        """

        md_path = output_dir / "meeting.md"

        choice = meeting.editors_choice
        selected_topic = meeting.topics[choice.index]

        lines = [
            "# Editorial Meeting",
            "",
            f"Date: {meeting_date.isoformat()}",
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
