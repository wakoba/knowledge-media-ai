from agents.athena import Athena
from agents.orion import Orion
from agents.polaris import Polaris
from agents.sophia import Sophia
from storage.history_reader import HistoryReader
from storage.meeting_repository import MeetingRepository
from storage.research_repository import ResearchRepository
from storage.review_repository import ReviewRepository
from storage.revised_review_repository import RevisedReviewRepository
from storage.revised_script_repository import RevisedScriptRepository
from storage.run_context import RunContext
from storage.run_summary_repository import RunSummaryRepository
from storage.script_repository import ScriptRepository
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
    7. すべての成果物をrun単位で保存
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
        }

        output_paths.update(revision_output_paths)

        return run_summary_repository.save(
            run_context=run_context,
            meeting=meeting_result,
            research=research_result,
            script=final_script_result,
            review=final_review_result,
            output_paths=output_paths,
        )
