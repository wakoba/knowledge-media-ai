from pathlib import Path

from llm import ask
from models.athena import AthenaScriptResult
from models.orion import OrionResearchResult


class Athena:
    """
    Project Polarisの台本AI。

    Orionのリサーチ結果を受け取り、
    YouTube動画用の台本を生成する。
    """

    def __init__(self):
        prompt_path = Path("athena/script_prompt.md")
        self.system_prompt = prompt_path.read_text(encoding="utf-8")

    def write_script(
        self,
        research: OrionResearchResult,
    ) -> AthenaScriptResult:
        """
        Orionのリサーチ結果をもとにYouTube台本を作成する。
        """

        research_json = research.model_dump_json(indent=2)

        user_prompt = f"""
以下はOrionが作成したリサーチ結果です。

このリサーチ結果をもとに、Project Polaris向けのYouTube台本を作成してください。

重要:
- 出力内容はすべて日本語にしてください。
- Orionのリサーチ結果にない数字を勝手に追加しないでください。
- 不確かな情報は断定しないでください。
- 視聴者が「世界って面白い」と感じる台本にしてください。
- 冒頭10秒で興味を引くHookを作ってください。
- 専門用語はやさしく説明してください。
- Athenaはライターです。研究結果を物語として伝えてください。
- estimated_duration_minutes は必ず 5〜15 の整数にしてください。
- estimated_duration_minutes に 0 は入れないでください。

Orion Research Result:
{research_json}
"""

        result = ask(
            self.system_prompt,
            user_prompt,
        )

        if result.get("estimated_duration_minutes", 0) < 1:
            result["estimated_duration_minutes"] = 8

        return AthenaScriptResult.model_validate(result)
