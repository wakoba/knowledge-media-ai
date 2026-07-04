from pydantic import BaseModel, Field


class NarrationSegment(BaseModel):
    """
    Narratorが作成する1シーン分のナレーション。
    """

    scene_number: int = Field(
        ge=1,
        description="対応するシーン番号"
    )

    section_heading: str = Field(
        description="対応するセクション見出し"
    )

    narration_text: str = Field(
        description="読み上げ用のナレーション本文"
    )

    subtitle_text: str = Field(
        description="字幕として使いやすい短めのテキスト"
    )

    pacing_notes: str = Field(
        description="読む速度や間の取り方に関するメモ"
    )

    voice_notes: str = Field(
        description="声のトーンや強調に関するメモ"
    )

    visual_sync_notes: str = Field(
        description="映像との同期に関するメモ"
    )


class NarrationScriptResult(BaseModel):
    """
    Narratorのナレーション原稿全体。
    """

    title: str = Field(
        description="ナレーション原稿のタイトル"
    )

    narration_style: str = Field(
        description="ナレーション全体の話し方・雰囲気"
    )

    estimated_duration_minutes: int = Field(
        ge=1,
        le=60,
        description="想定動画時間。単位は分"
    )

    opening_line: str = Field(
        description="冒頭の一言"
    )

    segments: list[NarrationSegment] = Field(
        min_length=1,
        description="シーンごとのナレーション"
    )

    closing_line: str = Field(
        description="締めの一言"
    )

    pronunciation_notes: list[str] = Field(
        default_factory=list,
        description="読み方に注意が必要な語句"
    )

    subtitle_notes: str = Field(
        description="字幕作成時の方針"
    )

    audio_production_notes: list[str] = Field(
        default_factory=list,
        description="音声制作上の補足メモ"
    )
