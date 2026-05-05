import json

from qa import answer_question


EVAL_PATH = "evaluation/qa_eval.json"


def contains_expected_keywords(
    answer: str,
    expected_keywords: list[str]
) -> bool:
    answer_lower = answer.lower()

    return all(keyword.lower() in answer_lower for keyword in expected_keywords)


def main() -> None:
    with open(EVAL_PATH, "r", encoding="utf-8") as file:
        eval_data = json.load(file)

    total = len(eval_data)
    correct = 0

    for item in eval_data:
        question = item["question"]
        expected_keywords = item["expected_keywords"]

        answer = answer_question(question)
        is_correct = contains_expected_keywords(answer, expected_keywords)

        if is_correct:
            correct += 1

        print("\nQuestion:", question)
        print("Answer:", answer)
        print("Expected:", expected_keywords)
        print("Correct:", is_correct)

    accuracy = correct / total if total > 0 else 0

    print("\n=== Evaluation Result ===")
    print(f"Correct: {correct}/{total}")
    print(f"Accuracy: {accuracy:.2f}")


if __name__ == "__main__":
    main()