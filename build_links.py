from io_utils import load_json_files, load_career_json, save_results, convert_to_triples
from linker import build_career_course_links

COURSE_JSON_FOLDER = "outputs/json/test"
CAREER_JSON_PATH = "data/careers/careers.json"
OUTPUT_PATH = "outputs/triples/career_linked_triples_test.json"


def main() -> None:
    course_jsons = load_json_files(COURSE_JSON_FOLDER)
    careers = load_career_json(CAREER_JSON_PATH)

    results = build_career_course_links(careers, course_jsons)
    triples = convert_to_triples(results)
    save_results(triples, OUTPUT_PATH)

    print(f"Total triples: {len(triples)}")


if __name__ == "__main__":
    main()