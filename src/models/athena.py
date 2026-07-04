from pydantic import BaseModel, Field


class ScriptSection(BaseModel):
    """
    Athenaが作成する台本の1セクション。
    """

    heading: str = Field(
        description="セクション見出し"
    )

    script: str = Field(
        description="このセクションで話す台本本文"
    )

    visual_ideas: list[str] = Field(
        default_factory=list,
        description="このセクションで使えそうな映像アイデア"
    )


class AthenaScriptResult(BaseModel):
    """
    Athenaの台本生成結果全体。

    Orionのリサーチ結果をもとに、
    YouTube動画用の台本として構造化する。
    """

    title: str = Field(
        description="動画タイトル"
    )

    video_concept: str = Field(
        description="動画全体のコンセプト"
    )

    target_viewer: str = Field(
        description="想定視聴者"
    )

    estimated_duration_minutes: int = Field(
        ge=1,
        le=60,
        description="想定動画時間。単位は分"
    )

    hook: str = Field(
        description="冒頭で視聴者を引き込むフック"
    )

    intro: str = Field(
        description="テーマ紹介の導入文"
    )

    sections: list[ScriptSection] = Field(
        min_length=1,
        description="台本本文のセクション一覧"
    )

    closing: str = Field(
        description="動画の締めの言葉"
    )

    thumbnail_ideas: list[str] = Field(
        default_factory=list,
        description="サムネイル案"
    )

    title_ideas: list[str] = Field(
        default_factory=list,
        description="別タイトル案"
    )

    short_summary: str = Field(
        description="動画内容の短い要約"
    )

    accuracy_notes: list[str] = Field(
        default_factory=list,
        description="正確性に関する注意点"
    )
