from pathlib import Path

from llm import ask
from models.athena import AthenaScriptResult
from models.orion import OrionResearchResult
from models.sophia import SophiaReviewResult


class Athena:
    """
    Project Polarisの台本AI。

    Orionのリサーチ結果を受け取り、
    YouTube動画用の台本を生成・修正する。
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

    def revise_script(
        self,
        research: OrionResearchResult,
        original_script: AthenaScriptResult,
        review: SophiaReviewResult,
    ) -> AthenaScriptResult:
        """
        Sophiaのレビュー結果をもとに、Athenaの台本を修正する。
        """

        if review.approved:
            return original_script

        research_json = research.model_dump_json(indent=2)
        original_script_json = original_script.model_dump_json(indent=2)
        review_json = review.model_dump_json(indent=2)

        user_prompt = f"""
以下はOrionのリサーチ結果、Athenaの初稿台本、Sophiaのレビュー結果です。

あなたはAthenaとして、Sophiaの指摘を反映した修正版台本を作成してください。

重要:
- 出力内容はすべて日本語にしてください。
- 台本全体の良さは維持してください。
- Sophiaの required_revisions は必ず反映してください。
- Sophiaの issues にある suggested_revision を反映してください。
- 強すぎる断定表現を緩和してください。
- 安全面の注意が必要な箇所には、明確な注意文を入れてください。
- Orionのリサーチ結果にない新しい数字や事実を追加しないでください。
- 不確かな情報は断定しないでください。
- estimated_duration_minutes は必ず 5〜15 の整数にしてください。
- estimated_duration_minutes に 0 は入れないでください。
- 返すのは修正版の台本JSONのみです。

Orion Research Result:
{research_json}

Original Athena Script:
{original_script_json}

Sophia Review:
{review_json}
"""

        result = ask(
            self.system_prompt,
            user_prompt,
        )

        if result.get("estimated_duration_minutes", 0) < 1:
            result["estimated_duration_minutes"] = original_script.estimated_duration_minutes or 8

        return AthenaScriptResult.model_validate(result)
