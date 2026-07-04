from pathlib import Path

from llm import ask
from models.athena import AthenaScriptResult
from models.orion import OrionResearchResult
from models.sophia import SophiaReviewResult


class Sophia:
    """
    Project Polarisのファクトチェック・編集レビューAI。

    Orionのリサーチ結果とAthenaの台本を照合し、
    正確性・誇張・誤解リスク・安全性を確認する。
    """

    def __init__(self):
        prompt_path = Path("sophia/factcheck_prompt.md")
        self.system_prompt = prompt_path.read_text(encoding="utf-8")

    def review(
        self,
        research: OrionResearchResult,
        script: AthenaScriptResult,
    ) -> SophiaReviewResult:
        """
        Orionのリサーチ結果とAthenaの台本をもとに、
        公開前レビューを行う。
        """

        research_json = research.model_dump_json(indent=2)
        script_json = script.model_dump_json(indent=2)

        user_prompt = f"""
以下はOrionが作成したリサーチ結果と、Athenaが作成したYouTube台本です。

あなたはSophiaとして、公開前レビューを行ってください。

重要:
- Orionのリサーチ内容とAthenaの台本が矛盾していないか確認してください。
- Athenaの台本に、強すぎる断定や誇張がないか確認してください。
- 数値表現がある場合、条件や前提が不足していないか確認してください。
- 視聴者が誤解しそうな表現がないか確認してください。
- 問題がある場合は approved を false にしてください。
- 問題がない場合のみ approved を true にしてください。
- 出力内容はすべて日本語にしてください。

Orion Research Result:
{research_json}

Athena Script Result:
{script_json}
"""

        result = ask(
            self.system_prompt,
            user_prompt,
        )

        return SophiaReviewResult.model_validate(result)
