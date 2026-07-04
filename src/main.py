from agents.polaris import Polaris
from storage.meeting_storage import MeetingStorage


def main():
    polaris = Polaris()
    result = polaris.generate_topics()
    
    storage = MeetingStorage()
    saved_paths = storage.save(result)

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

    choice = result.editors_choice
    selected_topic = result.topics[choice.index]

    print("🏆 Editor's Choice")
    print(selected_topic.title)
    print()
    print("Reason:")
    print(choice.reason)


if __name__ == "__main__":
    main()
