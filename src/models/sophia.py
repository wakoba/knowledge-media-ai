from pydantic import BaseModel, Field


class SophiaIssue(BaseModel):
    """
    Sophiaが検出した問題点1件。
    """

    type: str = Field(
        description="問題の種類。例: factual_accuracy, overstatement, numerical_claim, misunderstanding_risk"
    )

    severity: str = Field(
        description="問題の重大度。例: low, medium, high"
    )

    original_text: str = Field(
        description="問題がある元の表現"
    )

    problem: str = Field(
        description="なぜ問題なのか"
    )

    suggested_revision: str = Field(
        description="修正案"
    )


class SophiaReviewResult(BaseModel):
    """
    Sophiaのファクトチェック・編集レビュー結果全体。

    Athenaの台本を公開前に確認し、
    正確性・誇張・誤解リスク・表現の安全性を評価する。
    """

    approved: bool = Field(
        description="そのまま公開してよい場合はTrue。修正が必要な場合はFalse"
    )

    overall_assessment: str = Field(
        description="レビュー全体の総評"
    )

    risk_level: str = Field(
        description="全体のリスクレベル。例: low, medium, high"
    )

    issues: list[SophiaIssue] = Field(
        default_factory=list,
        description="検出された問題点の一覧"
    )

    required_revisions: list[str] = Field(
        default_factory=list,
        description="公開前に必ず修正すべき点"
    )

    optional_improvements: list[str] = Field(
        default_factory=list,
        description="必須ではないが改善するとよい点"
    )

    final_notes: str = Field(
        description="最終コメント"
    )
