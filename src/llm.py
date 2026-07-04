import json

from openai import OpenAI

from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)


def ask(system_prompt: str, user_prompt: str) -> dict:
    """
    OpenAIへ問い合わせを行い、
    JSONレスポンスをPythonのdictとして返す。
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

    try:
        return json.loads(response.output_text)

    except json.JSONDecodeError as e:
        raise ValueError(
            f"AIがJSONを返しませんでした。\n\n{response.output_text}"
        ) from e
