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
        """

        dates = self.repository.list_dates()
        recent_dates = dates[-limit:]

        meetings = []

        for meeting_date in recent_dates:
            meeting = self.repository.load_by_date(meeting_date)
            meetings.append(
                {
                    "date": meeting_date,
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
            meeting_date = item["date"]
            meeting = item["meeting"]
            choice = meeting.editors_choice
            selected_topic = meeting.topics[choice.index]

            lines.extend(
                [
                    f"## {meeting_date}",
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
