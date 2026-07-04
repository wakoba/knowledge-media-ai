from datetime import date
from pathlib import Path

from models.polaris import PolarisResult


class MeetingRepository:
    """
    Project Polarisの編集会議データを管理するRepository。

    保存:
    output/YYYY-MM-DD/run_HHMMSS/meeting.json
    output/YYYY-MM-DD/run_HHMMSS/meeting.md

    読み込み:
    旧形式 output/YYYY-MM-DD/meeting.json も読める。
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
        meeting: PolarisResult,
        meeting_date: date | None = None,
    ) -> dict[str, Path]:
        """
        編集会議結果をJSONとMarkdownで保存する。
        """

        output_dir = self._resolve_output_dir(meeting_date)
        output_dir.mkdir(parents=True, exist_ok=True)

        target_date = meeting_date or date.today()

        json_path = self._save_json(meeting, output_dir)
        md_path = self._save_markdown(meeting, output_dir, target_date)

        return {
            "json": json_path,
            "markdown": md_path,
        }

    def load_by_date(self, meeting_date: str) -> PolarisResult:
        """
        指定した日付の最新の編集会議結果を読み込む。

        例:
        repository.load_by_date("2026-07-04")
        """

        paths = self._meeting_paths_for_date(meeting_date)

        if not paths:
            raise FileNotFoundError(
                f"編集会議データが見つかりません: {meeting_date}"
            )

        return self.load_by_path(paths[-1])

    def load_by_path(self, json_path: Path | str) -> PolarisResult:
        """
        meeting.json のパスを指定して読み込む。
        """

        path = Path(json_path)

        if not path.exists():
            raise FileNotFoundError(
                f"編集会議データが見つかりません: {path}"
            )

        json_text = path.read_text(encoding="utf-8")

        return PolarisResult.model_validate_json(json_text)

    def list_dates(self) -> list[str]:
        """
        保存済みの編集会議日付一覧を返す。
        """

        dates = []

        for path in self.base_dir.iterdir():
            if not path.is_dir():
                continue

            if self._date_dir_has_meeting(path):
                dates.append(path.name)

        return sorted(dates)

    def list_meeting_paths(self) -> list[Path]:
        """
        保存済み meeting.json の一覧を返す。

        新形式:
        output/YYYY-MM-DD/run_HHMMSS/meeting.json

        旧形式:
        output/YYYY-MM-DD/meeting.json
        """

        meeting_paths = []

        for date_dir in sorted(self.base_dir.iterdir()):
            if not date_dir.is_dir():
                continue

            legacy_path = date_dir / "meeting.json"
            if legacy_path.exists():
                meeting_paths.append(legacy_path)

            for run_dir in sorted(date_dir.iterdir()):
                if not run_dir.is_dir():
                    continue

                run_meeting_path = run_dir / "meeting.json"
                if run_meeting_path.exists():
                    meeting_paths.append(run_meeting_path)

        return meeting_paths

    def load_latest(self) -> PolarisResult:
        """
        最新の編集会議結果を読み込む。
        """

        paths = self.list_meeting_paths()

        if not paths:
            raise FileNotFoundError(
                "保存済みの編集会議データがありません。"
            )

        return self.load_by_path(paths[-1])

    def _resolve_output_dir(
        self,
        meeting_date: date | None = None,
    ) -> Path:
        """
        保存先ディレクトリを決定する。

        RunContextがある場合:
        output/YYYY-MM-DD/run_HHMMSS/

        RunContextがない場合:
        output/YYYY-MM-DD/
        """

        if self.run_dir is not None:
            return self.run_dir

        target_date = meeting_date or date.today()

        return self.base_dir / target_date.isoformat()

    def _save_json(
        self,
        meeting: PolarisResult,
        output_dir: Path,
    ) -> Path:
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

    def _meeting_paths_for_date(self, meeting_date: str) -> list[Path]:
        date_dir = self.base_dir / meeting_date

        if not date_dir.exists():
            return []

        paths = []

        legacy_path = date_dir / "meeting.json"
        if legacy_path.exists():
            paths.append(legacy_path)

        for run_dir in sorted(date_dir.iterdir()):
            if not run_dir.is_dir():
                continue

            run_meeting_path = run_dir / "meeting.json"
            if run_meeting_path.exists():
                paths.append(run_meeting_path)

        return paths

    def _date_dir_has_meeting(self, date_dir: Path) -> bool:
        if (date_dir / "meeting.json").exists():
            return True

        for run_dir in date_dir.iterdir():
            if run_dir.is_dir() and (run_dir / "meeting.json").exists():
                return True

        return False
