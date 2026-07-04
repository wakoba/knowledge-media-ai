from pathlib import Path

from llm import ask
from models.polaris import PolarisResult


class Polaris:
    def __init__(self):
        prompt_path = Path("polaris/editor_prompt.md")
        self.system_prompt = prompt_path.read_text(encoding="utf-8")

    def generate_topics(self) -> PolarisResult:
        user_prompt = """
今日YouTubeで扱う価値のあるテーマを5件提案してください。
Project Polarisの理念に沿って、誰かに共有したくなる発見を選んでください。
出力内容はすべて日本語にしてください。
"""

        result = ask(
            self.system_prompt,
            user_prompt,
        )

        return PolarisResult.model_validate(result)
