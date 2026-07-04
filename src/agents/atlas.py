from pathlib import Path

from llm import ask
from models.athena import AthenaScriptResult
from models.atlas import AtlasVideoPlanResult


class Atlas:
    """
    Project Polarisの動画設計AI。

    final_scriptを受け取り、動画構成・映像指示・字幕方針を作成する。
    """

    def __init__(self):
        prompt_path = Path("atlas/video_plan_prompt.md")
        self.system_prompt = prompt_path.read_text(encoding="utf-8")

    def create_video_plan(
        self,
        final_script: AthenaScriptResult,
    ) -> AtlasVideoPlanResult:
        """
        最終台本をもとに動画制作プランを作成する。
        """

        final_script_json = final_script.model_dump_json(indent=2)

        user_prompt = f"""
以下はProject Polarisの最終台本です。

この台本をもとに、動画制作に使えるVideo Planを作成してください。

重要:
- 出力内容はすべて日本語にしてください。
- 台本にない新しい事実や数字を追加しないでください。
- 視聴者が理解しやすい映像構成にしてください。
- 映像は、図解・シンプルなアニメーション・抽象表現・安全なデモを中心にしてください。
- 著作権のある映像やブランド固有の素材を前提にしないでください。
- 危険な実験やレーザー・高温・薬品・電気などが関係する場合は、安全注意を入れてください。
- estimated_duration_minutes は必ず 1〜60 の整数にしてください。

Final Script:
{final_script_json}
"""

        result = ask(
            self.system_prompt,
            user_prompt,
        )

        if result.get("estimated_duration_minutes", 0) < 1:
            result["estimated_duration_minutes"] = final_script.estimated_duration_minutes

        return AtlasVideoPlanResult.model_validate(result)
