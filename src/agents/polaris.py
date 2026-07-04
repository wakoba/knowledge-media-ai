from pathlib import Path

from llm import ask
from models.polaris import PolarisResult


class Polaris:
    def __init__(self):
        prompt_path = Path("polaris/editor_prompt.md")
        self.system_prompt = prompt_path.read_text(encoding="utf-8")

    def generate_topics(self, history_summary: str | None = None) -> PolarisResult:
        history_text = history_summary or "過去の編集会議履歴はまだありません。"

        user_prompt = f"""
今日YouTubeで扱う価値のあるテーマを5件、日本語で提案してください。

Project Polarisの理念に沿って、誰かに共有したくなる発見を選んでください。
出力内容はすべて日本語にしてください。

以下は過去の編集会議履歴です。

{history_text}

重要:
- 過去に採用されたテーマと同じテーマは避けてください。
- 過去の候補テーマと近すぎるテーマも避けてください。
- ただし、全く別の切り口で明確に新しい学びがある場合のみ採用可能です。
- 採用理由では、なぜ過去テーマと重複しないのかも考慮してください。
"""

        result = ask(
            self.system_prompt,
            user_prompt,
        )

        return PolarisResult.model_validate(result)
