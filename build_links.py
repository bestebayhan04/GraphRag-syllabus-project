from linker import (
    load_json_files,
    load_career_json,
    build_course_topic_index,
    build_career_triples,
    save_linked_triples,
)


COURSE_JSON_FOLDER = "outputs/json"
CAREER_JSON_PATH = "data/careers/careers.json"
OUTPUT_PATH = "outputs/triples/career_linked_triples.json"


def main() -> None:
    course_jsons = load_json_files(COURSE_JSON_FOLDER)
    careers = load_career_json(CAREER_JSON_PATH)

    topic_to_courses = build_course_topic_index(course_jsons)
    triples = build_career_triples(careers, topic_to_courses)

    save_linked_triples(triples, OUTPUT_PATH)

    print(f"Total linked triples: {len(triples)}")


if __name__ == "__main__":
    main()