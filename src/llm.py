import json
from json import JSONDecodeError

from openai import OpenAI

from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)


def ask(system_prompt: str, user_prompt: str) -> dict:
    """
    OpenAIへ問い合わせを行い、
    JSONレスポンスをPythonのdictとして返す。

    1回目でJSONパースに失敗した場合は、
    AIにJSON修復を依頼して再パースする。
    """

    response = client.responses.create(
        model="gpt-5",
        input=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
    )

    raw_text = response.output_text

    try:
        return json.loads(raw_text)

    except JSONDecodeError:
        repaired_text = repair_json(raw_text)

        try:
            return json.loads(repaired_text)

        except JSONDecodeError as e:
            raise ValueError(
                "AIがJSONを返しませんでした。\n\n"
                "Original response:\n"
                f"{raw_text}\n\n"
                "Repaired response:\n"
                f"{repaired_text}"
            ) from e


def repair_json(broken_json: str) -> str:
    """
    壊れたJSON文字列をAIに修復させる。
    """

    repair_prompt = f"""
以下のテキストは、JSONとして返されるべき内容ですが、構文が壊れています。

あなたの仕事は、内容を変えずに、JSONとして有効な形へ修復することです。

ルール:
- Return ONLY valid JSON.
- Do not use Markdown.
- Do not include explanations.
- 内容は変更しないでください。
- 欠けているダブルクォート、カンマ、閉じカッコのみ修正してください。
- 日本語の閉じカギカッコ「」をJSON文字列の終端として使わないでください。
- JSONの文字列は必ず半角ダブルクォートで閉じてください。
- 改行を文字列内に直接入れないでください。

Broken JSON:
{broken_json}
"""

    response = client.responses.create(
        model="gpt-5",
        input=[
            {
                "role": "system",
                "content": "You repair invalid JSON. Return only valid JSON.",
            },
            {
                "role": "user",
                "content": repair_prompt,
            },
        ],
    )

    return response.output_text
