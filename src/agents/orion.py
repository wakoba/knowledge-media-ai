from pathlib import Path

from llm import ask
from models.orion import OrionResearchResult


class Orion:
    """
    Project PolarisのリサーチAI。

    Polarisが選んだテーマを受け取り、
    動画制作に使えるリサーチレポートを生成する。
    """

    def __init__(self):
        prompt_path = Path("orion/research_prompt.md")
        self.system_prompt = prompt_path.read_text(encoding="utf-8")

    def research(
        self,
        topic_title: str,
        topic_summary: str | None = None,
    ) -> OrionResearchResult:
        """
        指定されたテーマについてリサーチする。
        """

        summary_text = topic_summary or "概要は未指定です。"

        user_prompt = f"""
以下のテーマについて、Project Polarisのリサーチレポートを作成してください。

テーマ:
{topic_title}

概要:
{summary_text}

重要:
- 出力内容はすべて日本語にしてください。
- 正確性を重視してください。
- 不確かな内容は断定しないでください。
- Athenaが後で台本を書けるように、構成しやすい情報を整理してください。
- 視聴者が「誰かに話したくなる」発見を含めてください。
"""

        result = ask(
            self.system_prompt,
            user_prompt,
        )

        return OrionResearchResult.model_validate(result)
