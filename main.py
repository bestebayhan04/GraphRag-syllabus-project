import json
import os

from pdf_reader import extract_pdf_text, save_text_output
from llm_extractor import extract_syllabus_with_llm
from kg_builder import create_triples, save_triples


DATA_PATH = "data/syllabi"
JSON_OUTPUT_PATH = "outputs/json"


def save_json_output(filename: str, data: dict) -> str:
    os.makedirs(JSON_OUTPUT_PATH, exist_ok=True)

    base_name = os.path.splitext(filename)[0]
    output_path = os.path.join(JSON_OUTPUT_PATH, f"{base_name}.json")

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    return output_path


def main() -> None:
    os.makedirs("outputs/texts", exist_ok=True)
    os.makedirs("outputs/json", exist_ok=True)
    os.makedirs("outputs/triples", exist_ok=True)

    for filename in os.listdir(DATA_PATH):
        if not filename.lower().endswith(".pdf"):
            continue

        file_path = os.path.join(DATA_PATH, filename)

        print(f"\nProcessing PDF: {filename}")

        text = extract_pdf_text(file_path)
        text_output_path = save_text_output(filename, text)
        print(f"Saved text: {text_output_path}")

        structured_data = extract_syllabus_with_llm(text, source_file=filename)
        json_output_path = save_json_output(filename, structured_data)
        print(f"Saved JSON: {json_output_path}")

        triples = create_triples(structured_data)
        triples_output_path = save_triples(filename, triples)
        print(f"Saved triples: {triples_output_path}")

        print(f"Extracted triples: {len(triples)}")


if __name__ == "__main__":
    main()