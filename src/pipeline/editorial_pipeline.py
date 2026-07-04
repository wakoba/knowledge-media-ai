from agents.athena import Athena
from agents.atlas import Atlas
from agents.narrator import Narrator
from agents.orion import Orion
from agents.polaris import Polaris
from agents.sophia import Sophia
from storage.final_script_repository import FinalScriptRepository
from storage.history_reader import HistoryReader
from storage.meeting_repository import MeetingRepository
from storage.narration_repository import NarrationRepository
from storage.research_repository import ResearchRepository
from storage.review_repository import ReviewRepository
from storage.revised_review_repository import RevisedReviewRepository
from storage.revised_script_repository import RevisedScriptRepository
from storage.run_context import RunContext
from storage.run_summary_repository import RunSummaryRepository
from storage.script_repository import ScriptRepository
from storage.video_plan_repository import VideoPlanRepository
from utils.logger import setup_logger


class EditorialPipeline:
    """
    Project Polarisの編集パイプライン。

    実行内容:
    1. Polarisがテーマ候補を作成
    2. Orionが選定テーマをリサーチ
    3. Athenaが台本を作成
    4. Sophiaがレビュー
    5. 必要ならAthenaが最大2回まで修正
    6. Sophiaが修正版を再レビュー
    7. 最終台本をfinal_scriptとして保存
    8. Sophia承認済みならAtlasが動画設計を作成
    9. Narratorが読み上げ用ナレーション原稿を作成
    10. すべての成果物をrun単位で保存
    """

    def __init__(
        self,
        max_revision_rounds: int = 2,
    ):
        self.logger = setup_logger()
        self.max_revision_rounds = max_revision_rounds

    def run(self):
        try:
            self.logger.info("Project Polaris started")

            run_context = RunContext()

            self.logger.info("Run ID: %s", run_context.run_id)
            self.logger.info("Run directory: %s", run_context.run_dir)

            meeting_repository = MeetingRepository(
                run_dir=run_context.run_dir,
            )

            history_reader = HistoryReader(meeting_repository)
            history_summary = history_reader.build_summary(limit=5)

            self.logger.info("History summary generated")

            polaris = Polaris()
            meeting_result = polaris.generate_topics(
                history_summary=history_summary,
            )

            self.logger.info("Generated %s topics", len(meeting_result.topics))

            choice = meeting_result.editors_choice
            selected_topic = meeting_result.topics[choice.index]

            self.logger.info("Editor's Choice: %s", selected_topic.title)

            meeting_paths = meeting_repository.save(meeting_result)

            self.logger.info("Saved JSON: %s", meeting_paths["json"])
            self.logger.info("Saved Markdown: %s", meeting_paths["markdown"])

            self._print_run_header(
                run_context=run_context,
                meeting_paths=meeting_paths,
            )

            self._print_editorial_meeting(
                meeting_result=meeting_result,
                selected_topic=selected_topic,
                choice=choice,
            )

            research_result, research_paths = self._run_orion(
                run_context=run_context,
                selected_topic=selected_topic,
            )

            script_result, script_paths = self._run_athena(
                run_context=run_context,
                research_result=research_result,
            )

            review_result, review_paths = self._run_sophia_review(
                run_context=run_context,
                research_result=research_result,
                script_result=script_result,
            )

            (
                final_script_result,
                final_review_result,
                revision_output_paths,
            ) = self._run_revision_loop(
                run_context=run_context,
                research_result=research_result,
                initial_script_result=script_result,
                initial_review_result=review_result,
            )

            final_script_paths = self._save_final_script(
                run_context=run_context,
                final_script_result=final_script_result,
                final_review_result=final_review_result,
            )

            video_plan_result = None
            video_plan_paths = None
            narration_paths = None

            if final_review_result.approved:
                video_plan_result, video_plan_paths = self._run_atlas(
                    run_context=run_context,
                    final_script_result=final_script_result,
                )

                self.logger.info(
                    "Atlas video plan generated: %s",
                    video_plan_result.title,
                )

                narration_result, narration_paths = self._run_narrator(
                    run_context=run_context,
                    final_script_result=final_script_result,
                    video_plan_result=video_plan_result,
                )

                self.logger.info(
                    "Narration script generated: %s",
                    narration_result.title,
                )

            else:
                self.logger.info(
                    "Atlas and Narrator skipped because the final script was not approved"
                )

                print()
                print("Atlas and Narrator skipped:")
                print("- Final script is not approved by Sophia.")

            run_summary_path = self._save_run_summary(
                run_context=run_context,
                meeting_result=meeting_result,
                research_result=research_result,
                final_script_result=final_script_result,
                final_review_result=final_review_result,
                meeting_paths=meeting_paths,
                research_paths=research_paths,
                script_paths=script_paths,
                review_paths=review_paths,
                final_script_paths=final_script_paths,
                video_plan_paths=video_plan_paths,
                narration_paths=narration_paths,
                revision_output_paths=revision_output_paths,
            )

            self.logger.info("Saved Run Summary: %s", run_summary_path)

            print()
            print("Run summary saved:")
            print(f"- Markdown: {run_summary_path}")

            self.logger.info("Project Polaris completed successfully")

        except Exception as e:
            self.logger.exception("Project Polaris failed: %s", e)
            raise

    def _print_run_header(
        self,
        run_context,
        meeting_paths,
    ):
        print()
        print("Run:")
        print(f"- ID: {run_context.run_id}")
        print(f"- Directory: {run_context.run_dir}")

        print()
        print("Saved:")
        print(f"- JSON: {meeting_paths['json']}")
        print(f"- Markdown: {meeting_paths['markdown']}")

    def _print_editorial_meeting(
        self,
        meeting_result,
        selected_topic,
        choice,
    ):
        print("=" * 60)
        print("🌍 Project Polaris")
        print("Today's Editorial Meeting")
        print("=" * 60)

        for i, topic in enumerate(meeting_result.topics):
            print(f"{i + 1}. {topic.title}")
            print(f"   Score: {topic.curiosity_score}")
            print()

        print("🏆 Editor's Choice")
        print(selected_topic.title)
        print()
        print("Reason:")
        print(choice.reason)

    def _run_orion(
        self,
        run_context,
        selected_topic,
    ):
        print()
        print("=" * 60)
        print("🔭 Orion Research")
        print("=" * 60)

        orion = Orion()
        research_result = orion.research(
            topic_title=selected_topic.title,
            topic_summary=selected_topic.summary,
        )

        print("Overview:")
        print(research_result.overview)
        print()

        print("Key Facts:")
        for fact in research_result.key_facts:
            print(f"- {fact}")

        research_repository = ResearchRepository(
            run_dir=run_context.run_dir,
        )
        research_paths = research_repository.save(research_result)

        self.logger.info("Orion research completed")
        self.logger.info("Saved Research JSON: %s", research_paths["json"])
        self.logger.info("Saved Research Markdown: %s", research_paths["markdown"])

        print()
        print("Research saved:")
        print(f"- JSON: {research_paths['json']}")
        print(f"- Markdown: {research_paths['markdown']}")

        return research_result, research_paths

    def _run_athena(
        self,
        run_context,
        research_result,
    ):
        print()
        print("=" * 60)
        print("🦉 Athena Script")
        print("=" * 60)

        athena = Athena()
        script_result = athena.write_script(research_result)

        print("Title:")
        print(script_result.title)
        print()

        print("Hook:")
        print(script_result.hook)
        print()

        print("Sections:")
        for section in script_result.sections:
            print(f"- {section.heading}")

        script_repository = ScriptRepository(
            run_dir=run_context.run_dir,
        )
        script_paths = script_repository.save(script_result)

        self.logger.info("Athena script completed")
        self.logger.info("Script title: %s", script_result.title)
        self.logger.info("Saved Script JSON: %s", script_paths["json"])
        self.logger.info("Saved Script Markdown: %s", script_paths["markdown"])

        print()
        print("Script saved:")
        print(f"- JSON: {script_paths['json']}")
        print(f"- Markdown: {script_paths['markdown']}")

        return script_result, script_paths

    def _run_sophia_review(
        self,
        run_context,
        research_result,
        script_result,
    ):
        print()
        print("=" * 60)
        print("🛡️ Sophia Review")
        print("=" * 60)

        sophia = Sophia()
        review_result = sophia.review(
            research=research_result,
            script=script_result,
        )

        self._print_review_result(review_result)

        self.logger.info("Sophia review completed")
        self.logger.info("Sophia approved: %s", review_result.approved)
        self.logger.info("Sophia risk level: %s", review_result.risk_level)

        review_repository = ReviewRepository(
            run_dir=run_context.run_dir,
        )
        review_paths = review_repository.save(review_result)

        self.logger.info("Saved Review JSON: %s", review_paths["json"])
        self.logger.info("Saved Review Markdown: %s", review_paths["markdown"])

        print()
        print("Review saved:")
        print(f"- JSON: {review_paths['json']}")
        print(f"- Markdown: {review_paths['markdown']}")

        return review_result, review_paths

    def _run_revision_loop(
        self,
        run_context,
        research_result,
        initial_script_result,
        initial_review_result,
    ):
        final_script_result = initial_script_result
        final_review_result = initial_review_result

        revision_output_paths = {}

        current_script_result = initial_script_result
        current_review_result = initial_review_result

        athena = Athena()
        sophia = Sophia()

        revised_script_repository = RevisedScriptRepository(
            run_dir=run_context.run_dir,
        )
        revised_review_repository = RevisedReviewRepository(
            run_dir=run_context.run_dir,
        )

        for revision_round in range(1, self.max_revision_rounds + 1):
            if current_review_result.approved:
                if revision_round == 1:
                    self.logger.info(
                        "Athena revision skipped because Sophia approved the script"
                    )
                else:
                    self.logger.info(
                        "Athena revision loop stopped because Sophia approved the revised script"
                    )
                break

            print()
            print("=" * 60)
            print(f"🦉 Athena Revision v{revision_round}")
            print("=" * 60)

            revised_script_result = athena.revise_script(
                research=research_result,
                original_script=current_script_result,
                review=current_review_result,
            )

            current_script_result = revised_script_result
            final_script_result = revised_script_result

            print("Revised Title:")
            print(revised_script_result.title)
            print()

            print("Revised Hook:")
            print(revised_script_result.hook)
            print()

            print("Revised Sections:")
            for section in revised_script_result.sections:
                print(f"- {section.heading}")

            revised_script_paths = revised_script_repository.save(
                revised_script_result,
                revision_number=revision_round,
            )

            revision_output_paths[
                f"revised_script_v{revision_round}"
            ] = revised_script_paths

            self.logger.info("Athena revision v%s completed", revision_round)
            self.logger.info("Revised Script title: %s", revised_script_result.title)
            self.logger.info(
                "Saved Revised Script JSON: %s",
                revised_script_paths["json"],
            )
            self.logger.info(
                "Saved Revised Script Markdown: %s",
                revised_script_paths["markdown"],
            )

            print()
            print("Revised script saved:")
            print(f"- JSON: {revised_script_paths['json']}")
            print(f"- Markdown: {revised_script_paths['markdown']}")

            print()
            print("=" * 60)
            print(f"🛡️ Sophia Re-review v{revision_round}")
            print("=" * 60)

            revised_review_result = sophia.review(
                research=research_result,
                script=revised_script_result,
            )

            current_review_result = revised_review_result
            final_review_result = revised_review_result

            self._print_review_result(revised_review_result)

            revised_review_paths = revised_review_repository.save(
                revised_review_result,
                revision_number=revision_round,
            )

            revision_output_paths[
                f"revised_review_v{revision_round}"
            ] = revised_review_paths

            self.logger.info("Sophia re-review v%s completed", revision_round)
            self.logger.info(
                "Sophia re-review approved: %s",
                revised_review_result.approved,
            )
            self.logger.info(
                "Sophia re-review risk level: %s",
                revised_review_result.risk_level,
            )
            self.logger.info(
                "Saved Revised Review JSON: %s",
                revised_review_paths["json"],
            )
            self.logger.info(
                "Saved Revised Review Markdown: %s",
                revised_review_paths["markdown"],
            )

            print()
            print("Revised review saved:")
            print(f"- JSON: {revised_review_paths['json']}")
            print(f"- Markdown: {revised_review_paths['markdown']}")

        return final_script_result, final_review_result, revision_output_paths

    def _print_review_result(
        self,
        review_result,
    ):
        print("Approved:")
        print(review_result.approved)
        print()

        print("Risk Level:")
        print(review_result.risk_level)
        print()

        print("Overall Assessment:")
        print(review_result.overall_assessment)
        print()

        if review_result.issues:
            print("Issues:")
            for issue in review_result.issues:
                print(f"- [{issue.severity}] {issue.type}")
                print(f"  Original: {issue.original_text}")
                print(f"  Problem: {issue.problem}")
                print(f"  Suggested: {issue.suggested_revision}")
                print()
        else:
            print("Issues:")
            print("- No major issues found.")

    def _save_final_script(
        self,
        run_context,
        final_script_result,
        final_review_result,
    ):
        final_script_repository = FinalScriptRepository(
            run_dir=run_context.run_dir,
        )

        final_script_paths = final_script_repository.save(
            script=final_script_result,
            review=final_review_result,
        )

        self.logger.info("Saved Final Script JSON: %s", final_script_paths["json"])
        self.logger.info(
            "Saved Final Script Markdown: %s",
            final_script_paths["markdown"],
        )

        print()
        print("Final script saved:")
        print(f"- JSON: {final_script_paths['json']}")
        print(f"- Markdown: {final_script_paths['markdown']}")

        return final_script_paths

    def _run_atlas(
        self,
        run_context,
        final_script_result,
    ):
        print()
        print("=" * 60)
        print("🎬 Atlas Video Plan")
        print("=" * 60)

        atlas = Atlas()
        video_plan_result = atlas.create_video_plan(
            final_script=final_script_result,
        )

        print("Title:")
        print(video_plan_result.title)
        print()

        print("Visual Style:")
        print(video_plan_result.visual_style)
        print()

        print("Scene Plan:")
        for scene in video_plan_result.scene_plan:
            print(f"- Scene {scene.scene_number}: {scene.section_heading}")

        video_plan_repository = VideoPlanRepository(
            run_dir=run_context.run_dir,
        )

        video_plan_paths = video_plan_repository.save(video_plan_result)

        self.logger.info("Atlas video plan completed")
        self.logger.info("Saved Video Plan JSON: %s", video_plan_paths["json"])
        self.logger.info(
            "Saved Video Plan Markdown: %s",
            video_plan_paths["markdown"],
        )

        print()
        print("Video plan saved:")
        print(f"- JSON: {video_plan_paths['json']}")
        print(f"- Markdown: {video_plan_paths['markdown']}")

        return video_plan_result, video_plan_paths

    def _run_narrator(
        self,
        run_context,
        final_script_result,
        video_plan_result,
    ):
        print()
        print("=" * 60)
        print("🎙️ Narrator Script")
        print("=" * 60)

        narrator = Narrator()
        narration_result = narrator.create_narration_script(
            final_script=final_script_result,
            video_plan=video_plan_result,
        )

        print("Title:")
        print(narration_result.title)
        print()

        print("Narration Style:")
        print(narration_result.narration_style)
        print()

        print("Segments:")
        for segment in narration_result.segments:
            print(f"- Scene {segment.scene_number}: {segment.section_heading}")

        narration_repository = NarrationRepository(
            run_dir=run_context.run_dir,
        )

        narration_paths = narration_repository.save(narration_result)

        self.logger.info("Narrator script completed")
        self.logger.info("Saved Narration JSON: %s", narration_paths["json"])
        self.logger.info(
            "Saved Narration Markdown: %s",
            narration_paths["markdown"],
        )

        print()
        print("Narration script saved:")
        print(f"- JSON: {narration_paths['json']}")
        print(f"- Markdown: {narration_paths['markdown']}")

        return narration_result, narration_paths

    def _save_run_summary(
        self,
        run_context,
        meeting_result,
        research_result,
        final_script_result,
        final_review_result,
        meeting_paths,
        research_paths,
        script_paths,
        review_paths,
        final_script_paths,
        video_plan_paths,
        narration_paths,
        revision_output_paths,
    ):
        run_summary_repository = RunSummaryRepository(
            run_dir=run_context.run_dir,
        )

        output_paths = {
            "meeting": meeting_paths,
            "research": research_paths,
            "script": script_paths,
            "review": review_paths,
            "final_script": final_script_paths,
        }

        if video_plan_paths is not None:
            output_paths["video_plan"] = video_plan_paths

        if narration_paths is not None:
            output_paths["narration_script"] = narration_paths

        output_paths.update(revision_output_paths)

        return run_summary_repository.save(
            run_context=run_context,
            meeting=meeting_result,
            research=research_result,
            script=final_script_result,
            review=final_review_result,
            output_paths=output_paths,
        )
