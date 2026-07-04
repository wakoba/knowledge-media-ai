from pydantic import BaseModel, Field


class Topic(BaseModel):
    """
    Polarisが提案するテーマ1件
    """

    title: str = Field(description="テーマのタイトル")
    summary: str = Field(description="テーマ概要")
    value: str = Field(description="取り上げる価値")
    audience: str = Field(description="想定視聴者")
    education: str = Field(description="教育的価値")
    curiosity_score: int = Field(
        ge=0,
        le=100,
        description="好奇心スコア（0〜100）"
    )
    reason: str = Field(description="採用理由")


class EditorsChoice(BaseModel):
    """
    編集長が最終的に選んだテーマ
    """

    index: int = Field(
        ge=0,
        le=4,
        description="topics内のインデックス（0〜4）"
    )

    reason: str = Field(description="選定理由")


class PolarisResult(BaseModel):
    """
    Polarisの出力全体
    """

    topics: list[Topic]
    editors_choice: EditorsChoice
