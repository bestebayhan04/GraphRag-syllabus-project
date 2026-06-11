import json
import os
from typing import Any, Dict, List


def load_json_files(folder_path: str) -> List[Dict[str, Any]]:
    """Loads all JSON files from a folder and returns them as a list of dicts."""
    items = []
    if not os.path.exists(folder_path):
        return items
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            path = os.path.join(folder_path, filename)
            with open(path, "r", encoding="utf-8") as file:
                items.append(json.load(file))
    return items


def load_career_json(path: str) -> List[Dict[str, Any]]:
    """Loads the careers JSON file."""
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_results(data: Any, output_path: str) -> None:
    """Saves any JSON-serializable data to the given output path."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    print(f"Saved to: {output_path}")


def convert_to_triples(results: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Converts linker output into a flat list of knowledge graph triples."""
    triples = []
    for result in results:
        career = result["career"]
        skill_course_map = result["skill_course_map"]

        for skill, courses in skill_course_map.items():
            triples.append({
                "subject": career,
                "relation": "REQUIRES_SKILL",
                "object": skill,
                "subject_type": "Career",
                "object_type": "Skill"
            })
            for course in courses:
                triples.append({
                    "subject": skill,
                    "relation": "TAUGHT_IN",
                    "object": course,
                    "subject_type": "Skill",
                    "object_type": "Course"
                })


    return triples