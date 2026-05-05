from qa import answer_question


def main() -> None:
    print("Graph QA is ready. Type 'exit' to quit.")

    while True:
        question = input("\nAsk a question: ")

        if question.lower() in ["exit", "quit"]:
            break

        answer = answer_question(question)
        print(answer)


if __name__ == "__main__":
    main()