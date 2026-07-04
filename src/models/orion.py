from pydantic import BaseModel, Field


class OrionResearchResult(BaseModel):
    """
    Orionのリサーチ結果全体。
    Polarisが選んだテーマについて、Athenaが台本を書けるように
    調査内容を構造化して返す。
    """

    topic_title: str = Field(
        description="調査対象のテーマタイトル"
    )

    overview: str = Field(
        description="テーマ全体の概要"
    )

    key_facts: list[str] = Field(
        min_length=1,
        description="重要な事実の一覧"
    )

    mechanism: str = Field(
        description="仕組みや原理の説明"
    )

    why_it_matters: str = Field(
        description="なぜこのテーマが重要なのか"
    )

    common_misunderstandings: list[str] = Field(
        default_factory=list,
        description="誤解されやすい点"
    )

    examples: list[str] = Field(
        default_factory=list,
        description="動画で使える具体例"
    )

    story_angles: list[str] = Field(
        default_factory=list,
        description="動画構成に使える切り口"
    )

    viewer_takeaways: list[str] = Field(
        default_factory=list,
        description="視聴者が持ち帰れる学び"
    )

    open_question: str = Field(
        description="動画の最後に残せる問い"
    )

    research_notes: str = Field(
        description="補足メモ、注意点、今後深掘りすべき点"
    )
