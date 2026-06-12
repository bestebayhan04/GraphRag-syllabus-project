import argparse
from read_data import download_all, read_career_files, read_course_file
from linker import build_career_course_links, convert_to_triples

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--build-links", action="store_true")
    parser.add_argument("--build-graph", action="store_true")
    parser.add_argument("--evaluate", action="store_true")
    args = parser.parse_args()

    download_all()
    careers = read_career_files() 
    courses = read_course_file()

    if args.build_links:
        results = build_career_course_links(careers, courses)
        triples = convert_to_triples(results)

    if args.build_graph:
        pass

    if args.evaluate:
        pass
if __name__ == "__main__":
    main()