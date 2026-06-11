import argparse
from read_data import download_all, read_career_files, read_course_file
# from knowledge_graph import query_graph  # to be implemented


def parse_args():
    parser = argparse.ArgumentParser(description="Career-Course Knowledge Graph Query Tool")
    parser.add_argument("query", type=str, help="Your career or skill query")
    parser.add_argument("--top-k", type=int, default=5, help="Number of results to return")
    return parser.parse_args()


def main():
    args = parse_args()

    download_all()
    careers = read_career_files()
    courses = read_course_file()

    # result = query_graph(args.query, careers, courses, top_k=args.top_k)
    # print(result)


if __name__ == "__main__":
    main()