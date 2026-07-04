from pathlib import Path

from storage.meeting_repository import MeetingRepository


class HistoryReader:
    """
    過去の編集会議履歴を読み取り、
    Polarisに渡すための履歴サマリーを作るクラス。
    """

    def __init__(self, repository: MeetingRepository):
        self.repository = repository

    def get_recent_meetings(self, limit: int = 5):
        """
        直近の編集会議を取得する。
        日付単位ではなく、run単位で取得する。
        """

        paths = self.repository.list_meeting_paths()
        recent_paths = paths[-limit:]

        meetings = []

        for path in recent_paths:
            meeting = self.repository.load_by_path(path)

            meetings.append(
                {
                    "label": self._build_label(path),
                    "meeting": meeting,
                }
            )

        return meetings

    def build_summary(self, limit: int = 5) -> str:
        """
        Polarisに渡すための履歴サマリーを作成する。
        """

        recent_meetings = self.get_recent_meetings(limit=limit)

        if not recent_meetings:
            return "過去の編集会議履歴はまだありません。"

        lines = [
            "以下は、最近のProject Polaris編集会議の履歴です。",
            "同じテーマや近すぎるテーマを避け、新しい発見につながるテーマを選んでください。",
            "",
        ]

        for item in recent_meetings:
            label = item["label"]
            meeting = item["meeting"]
            choice = meeting.editors_choice
            selected_topic = meeting.topics[choice.index]

            lines.extend(
                [
                    f"## {label}",
                    f"- 採用テーマ: {selected_topic.title}",
                    f"- 選定理由: {choice.reason}",
                    "",
                    "候補テーマ:",
                ]
            )

            for topic in meeting.topics:
                lines.append(
                    f"- {topic.title}（Score: {topic.curiosity_score}）"
                )

            lines.append("")

        return "\n".join(lines)

    def _build_label(self, path: Path) -> str:
        """
        履歴表示用のラベルを作る。

        新形式:
        2026-07-04 / run_180955

        旧形式:
        2026-07-04
        """

        try:
            relative_path = path.relative_to(self.repository.base_dir)
        except ValueError:
            return str(path)

        parts = relative_path.parts

        if len(parts) >= 3:
            return f"{parts[0]} / {parts[1]}"

        if len(parts) >= 1:
            return parts[0]

        return str(path)
