import os
import json
from typing import Any, Dict, List


def normalize_text(text: str) -> str:
    return text.strip().title()


def normalize_course(code: str) -> str:
    return code.replace(" ", "").upper()


def create_triples(data: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Convert structured course JSON into graph triples.
    """
    triples = []

    course = data.get("course_code")

    if not course:
        return triples

    course = normalize_course(course)

    for topic in data.get("topics", []):
        triples.append({
            "subject": course,
            "relation": "HAS_TOPIC",
            "object": normalize_text(topic),
            "subject_type": "Course",
            "object_type": "Topic"
        })

    for prereq in data.get("prerequisites", []):
        triples.append({
            "subject": course,
            "relation": "HAS_PREREQ",
            "object": normalize_course(prereq),
            "subject_type": "Course",
            "object_type": "Course"
        })

    for coreq in data.get("corequisites", []):
        triples.append({
            "subject": course,
            "relation": "HAS_COREQ",
            "object": normalize_course(coreq),
            "subject_type": "Course",
            "object_type": "Course"
        })

    return triples


def save_triples(
    filename: str,
    triples: List[Dict[str, str]],
    output_dir: str = "outputs/triples"
) -> str:
    os.makedirs(output_dir, exist_ok=True)

    base_name = os.path.splitext(filename)[0]
    path = os.path.join(output_dir, f"{base_name}_triples.json")

    with open(path, "w", encoding="utf-8") as file:
        json.dump(triples, file, indent=4, ensure_ascii=False)

    return path


def process_json_file(json_path: str) -> List[Dict[str, str]]:
    with open(json_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    return create_triples(data)