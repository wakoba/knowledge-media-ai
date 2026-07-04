from agents.polaris import Polaris
from agents.orion import Orion
from storage.history_reader import HistoryReader
from storage.research_repository import ResearchRepository
from storage.meeting_repository import MeetingRepository
from utils.logger import setup_logger


def main():
    logger = setup_logger()

    try:
        logger.info("Project Polaris started")

        repository = MeetingRepository()

        history_reader = HistoryReader(repository)
        history_summary = history_reader.build_summary(limit=5)

        logger.info("History summary generated")

        polaris = Polaris()
        result = polaris.generate_topics(history_summary=history_summary)

        logger.info("Generated %s topics", len(result.topics))

        choice = result.editors_choice
        selected_topic = result.topics[choice.index]

        logger.info("Editor's Choice: %s", selected_topic.title)

        saved_paths = repository.save(result)

        logger.info("Saved JSON: %s", saved_paths["json"])
        logger.info("Saved Markdown: %s", saved_paths["markdown"])

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
            
        research_repository = ResearchRepository()
        research_paths = research_repository.save(research_result)

        logger.info("Orion research completed")
        logger.info("Saved Research JSON: %s", research_paths["json"])
        logger.info("Saved Research Markdown: %s", research_paths["markdown"])

        print()
        print("Research saved:")
        print(f"- JSON: {research_paths['json']}")
        print(f"- Markdown: {research_paths['markdown']}")

        logger.info("Project Polaris completed successfully")

    except Exception as e:
        logger.exception("Project Polaris failed: %s", e)
        raise


if __name__ == "__main__":
    main()
