from pydantic import BaseModel, Field


class AtlasScenePlan(BaseModel):
    """
    Atlasが作成する1シーン分の動画設計。
    """

    scene_number: int = Field(
        ge=1,
        description="シーン番号"
    )

    section_heading: str = Field(
        description="対応する台本セクション見出し"
    )

    narration_summary: str = Field(
        description="このシーンで語る内容の要約"
    )

    visual_description: str = Field(
        description="映像・アニメーション・図解の説明"
    )

    on_screen_text: str = Field(
        description="画面に表示する短いテキスト"
    )

    asset_type: str = Field(
        description="推奨素材タイプ。例: animation, diagram, stock_style, text, simple_demo"
    )

    editing_notes: str = Field(
        description="編集上の注意点"
    )

    safety_notes: str = Field(
        default="",
        description="安全上の注意点。不要な場合は空文字"
    )


class AtlasVideoPlanResult(BaseModel):
    """
    Atlasの動画設計結果全体。
    """

    title: str = Field(
        description="動画タイトル"
    )

    video_concept: str = Field(
        description="動画全体のコンセプト"
    )

    estimated_duration_minutes: int = Field(
        ge=1,
        le=60,
        description="想定動画時間。単位は分"
    )

    visual_style: str = Field(
        description="映像全体のスタイル"
    )

    target_viewer: str = Field(
        description="想定視聴者"
    )

    opening_visual: str = Field(
        description="冒頭映像の案"
    )

    scene_plan: list[AtlasScenePlan] = Field(
        min_length=1,
        description="シーンごとの動画設計"
    )

    b_roll_ideas: list[str] = Field(
        default_factory=list,
        description="B-roll素材案"
    )

    diagram_ideas: list[str] = Field(
        default_factory=list,
        description="図解・アニメーション案"
    )

    subtitle_direction: str = Field(
        description="字幕の方針"
    )

    narration_direction: str = Field(
        description="ナレーションの方針"
    )

    thumbnail_direction: str = Field(
        description="サムネイル方針"
    )

    production_notes: list[str] = Field(
        default_factory=list,
        description="制作上の補足メモ"
    )
