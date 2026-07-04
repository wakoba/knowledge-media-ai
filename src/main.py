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


def main():
    logger = setup_logger()

    try:
        logger.info("Project Polaris started")

        # 1回の実行単位を作成
        run_context = RunContext()

        logger.info("Run ID: %s", run_context.run_id)
        logger.info("Run directory: %s", run_context.run_dir)

        # 編集会議の保存・履歴読み込み用Repository
        meeting_repository = MeetingRepository(
            run_dir=run_context.run_dir,
        )

        # 過去の編集会議履歴を読み込む
        history_reader = HistoryReader(meeting_repository)
        history_summary = history_reader.build_summary(limit=5)

        logger.info("History summary generated")

        # Polaris: テーマ選定
        polaris = Polaris()
        result = polaris.generate_topics(
            history_summary=history_summary,
        )

        logger.info("Generated %s topics", len(result.topics))

        choice = result.editors_choice
        selected_topic = result.topics[choice.index]

        logger.info("Editor's Choice: %s", selected_topic.title)

        # 編集会議結果を保存
        saved_paths = meeting_repository.save(result)

        logger.info("Saved JSON: %s", saved_paths["json"])
        logger.info("Saved Markdown: %s", saved_paths["markdown"])

        print()
        print("Run:")
        print(f"- ID: {run_context.run_id}")
        print(f"- Directory: {run_context.run_dir}")

        print()
        print("Saved:")
        print(f"- JSON: {saved_paths['json']}")
        print(f"- Markdown: {saved_paths['markdown']}")

        print("=" * 60)
        print("🌍 Project Polaris")
        print("Today's Editorial Meeting")
        print("=" * 60)

        for i, topic in enumerate(result.topics):
            print(f"{i + 1}. {topic.title}")
            print(f"   Score: {topic.curiosity_score}")
            print()

        print("🏆 Editor's Choice")
        print(selected_topic.title)
        print()
        print("Reason:")
        print(choice.reason)

        # Orion: リサーチ
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

        logger.info("Orion research completed")
        logger.info("Saved Research JSON: %s", research_paths["json"])
        logger.info("Saved Research Markdown: %s", research_paths["markdown"])

        print()
        print("Research saved:")
        print(f"- JSON: {research_paths['json']}")
        print(f"- Markdown: {research_paths['markdown']}")

        # Athena: 台本作成
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

        logger.info("Athena script completed")
        logger.info("Script title: %s", script_result.title)
        logger.info("Saved Script JSON: %s", script_paths["json"])
        logger.info("Saved Script Markdown: %s", script_paths["markdown"])

        print()
        print("Script saved:")
        print(f"- JSON: {script_paths['json']}")
        print(f"- Markdown: {script_paths['markdown']}")

        # Sophia: ファクトチェック・公開前レビュー
        print()
        print("=" * 60)
        print("🛡️ Sophia Review")
        print("=" * 60)

        sophia = Sophia()
        review_result = sophia.review(
            research=research_result,
            script=script_result,
        )

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

        logger.info("Sophia review completed")
        logger.info("Sophia approved: %s", review_result.approved)
        logger.info("Sophia risk level: %s", review_result.risk_level)

        # Sophiaレビュー結果を保存
        review_repository = ReviewRepository(
            run_dir=run_context.run_dir,
        )
        review_paths = review_repository.save(review_result)

        logger.info("Saved Review JSON: %s", review_paths["json"])
        logger.info("Saved Review Markdown: %s", review_paths["markdown"])

        print()
        print("Review saved:")
        print(f"- JSON: {review_paths['json']}")
        print(f"- Markdown: {review_paths['markdown']}")

        # Athena Revision Loop + Sophia Re-review
        final_script_result = script_result
        final_review_result = review_result

        revision_output_paths = {}

        max_revision_rounds = 2
        current_script_result = script_result
        current_review_result = review_result

        revised_script_repository = RevisedScriptRepository(
            run_dir=run_context.run_dir,
        )
        revised_review_repository = RevisedReviewRepository(
            run_dir=run_context.run_dir,
        )

        for revision_round in range(1, max_revision_rounds + 1):
            if current_review_result.approved:
                if revision_round == 1:
                    logger.info(
                        "Athena revision skipped because Sophia approved the script"
                    )
                else:
                    logger.info(
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

            logger.info("Athena revision v%s completed", revision_round)
            logger.info("Revised Script title: %s", revised_script_result.title)
            logger.info(
                "Saved Revised Script JSON: %s",
                revised_script_paths["json"],
            )
            logger.info(
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

            print("Approved:")
            print(revised_review_result.approved)
            print()

            print("Risk Level:")
            print(revised_review_result.risk_level)
            print()

            print("Overall Assessment:")
            print(revised_review_result.overall_assessment)
            print()

            if revised_review_result.issues:
                print("Issues:")
                for issue in revised_review_result.issues:
                    print(f"- [{issue.severity}] {issue.type}")
                    print(f"  Original: {issue.original_text}")
                    print(f"  Problem: {issue.problem}")
                    print(f"  Suggested: {issue.suggested_revision}")
                    print()
            else:
                print("Issues:")
                print("- No major issues found.")

            revised_review_paths = revised_review_repository.save(
                revised_review_result,
                revision_number=revision_round,
            )

            revision_output_paths[
                f"revised_review_v{revision_round}"
            ] = revised_review_paths

            logger.info("Sophia re-review v%s completed", revision_round)
            logger.info(
                "Sophia re-review approved: %s",
                revised_review_result.approved,
            )
            logger.info(
                "Sophia re-review risk level: %s",
                revised_review_result.risk_level,
            )
            logger.info(
                "Saved Revised Review JSON: %s",
                revised_review_paths["json"],
            )
            logger.info(
                "Saved Revised Review Markdown: %s",
                revised_review_paths["markdown"],
            )

            print()
            print("Revised review saved:")
            print(f"- JSON: {revised_review_paths['json']}")
            print(f"- Markdown: {revised_review_paths['markdown']}")

        # Run Summary: 1回の実行結果をまとめる
        run_summary_repository = RunSummaryRepository(
            run_dir=run_context.run_dir,
        )

        output_paths = {
            "meeting": saved_paths,
            "research": research_paths,
            "script": script_paths,
            "review": review_paths,
        }

        output_paths.update(revision_output_paths)

        run_summary_path = run_summary_repository.save(
            run_context=run_context,
            meeting=result,
            research=research_result,
            script=final_script_result,
            review=final_review_result,
            output_paths=output_paths,
        )

        logger.info("Saved Run Summary: %s", run_summary_path)

        print()
        print("Run summary saved:")
        print(f"- Markdown: {run_summary_path}")

        logger.info("Project Polaris completed successfully")

    except Exception as e:
        logger.exception("Project Polaris failed: %s", e)
        raise


if __name__ == "__main__":
    main()
