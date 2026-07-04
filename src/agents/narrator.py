from pathlib import Path

from llm import ask
from models.athena import AthenaScriptResult
from models.atlas import AtlasVideoPlanResult
from models.narrator import NarrationScriptResult


class Narrator:
    """
    Project PolarisのナレーションAI。

    final_scriptとvideo_planを受け取り、
    読み上げ用のナレーション原稿を作成する。
    """

    def __init__(self):
        prompt_path = Path("narrator/narration_prompt.md")
        self.system_prompt = prompt_path.read_text(encoding="utf-8")

    def create_narration_script(
        self,
        final_script: AthenaScriptResult,
        video_plan: AtlasVideoPlanResult,
    ) -> NarrationScriptResult:
        """
        最終台本と動画設計をもとにナレーション原稿を作成する。
        """

        final_script_json = final_script.model_dump_json(indent=2)
        video_plan_json = video_plan.model_dump_json(indent=2)

        user_prompt = f"""
以下はProject Polarisの最終台本とAtlasの動画設計です。

この2つをもとに、実際に読み上げるためのナレーション原稿を作成してください。

重要:
- 出力内容はすべて日本語にしてください。
- final_scriptとvideo_planにない新しい事実や数字を追加しないでください。
- 読み上げたときに自然な日本語にしてください。
- 字幕化しやすいように、長すぎる文を避けてください。
- 専門用語には必要に応じて読み方メモを入れてください。
- pronunciation_notes は必ず文字列の配列にしてください。
- pronunciation_notes に object/dict は入れないでください。
- 例: "ミウラ折り：みうらおり"
- 安全注意が必要な内容は、ナレーション内でも明確に注意してください。
- estimated_duration_minutes は必ず 1〜60 の整数にしてください。

Final Script:
{final_script_json}

Atlas Video Plan:
{video_plan_json}
"""

        result = ask(
            self.system_prompt,
            user_prompt,
        )

        result = self._normalize_result(
            result=result,
            final_script=final_script,
        )

        return NarrationScriptResult.model_validate(result)

    def _normalize_result(
        self,
        result: dict,
        final_script: AthenaScriptResult,
    ) -> dict:
        """
        Narratorの出力をPydantic検証前に安全な形へ整える。

        特に pronunciation_notes は、
        AIが dict 形式で返すことがあるため、文字列配列へ変換する。
        """

        if result.get("estimated_duration_minutes", 0) < 1:
            result["estimated_duration_minutes"] = (
                final_script.estimated_duration_minutes
            )

        result["pronunciation_notes"] = self._normalize_pronunciation_notes(
            result.get("pronunciation_notes", [])
        )

        return result

    def _normalize_pronunciation_notes(
        self,
        pronunciation_notes,
    ) -> list[str]:
        """
        pronunciation_notes を list[str] に統一する。

        想定する入力:
        - ["ミウラ折り：みうらおり"]
        - [{"term": "ミウラ折り", "reading": "みうらおり"}]
        """

        if not pronunciation_notes:
            return []

        normalized_notes = []

        for note in pronunciation_notes:
            if isinstance(note, str):
                normalized_notes.append(note)
                continue

            if isinstance(note, dict):
                term = note.get("term", "")
                reading = note.get("reading", "")

                if term and reading:
                    normalized_notes.append(f"{term}：{reading}")
                elif term:
                    normalized_notes.append(str(term))
                elif reading:
                    normalized_notes.append(str(reading))
                else:
                    normalized_notes.append(str(note))

                continue

            normalized_notes.append(str(note))

        return normalized_notes
