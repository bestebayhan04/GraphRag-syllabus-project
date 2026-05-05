import json
import os
from typing import Any, Dict, List, Set


def normalize_topic(topic: str) -> str:
    aliases = {
        "ml": "Machine Learning",
        "machine-learning": "Machine Learning",
        "machine learning": "Machine Learning",
        "ai": "Artificial Intelligence",
        "artificial intelligence": "Artificial Intelligence",
        "dl": "Deep Learning",
        "deep-learning": "Deep Learning",
        "deep learning": "Deep Learning",
        "nn": "Neural Network",
        "neural networks": "Neural Network",
        "neural network": "Neural Network",
    }

    cleaned = topic.strip().lower()
    return aliases.get(cleaned, cleaned.title())


def load_json_files(folder_path: str) -> List[Dict[str, Any]]:
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
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def build_course_topic_index(
    course_jsons: List[Dict[str, Any]]
) -> Dict[str, Set[str]]:
    topic_to_courses: Dict[str, Set[str]] = {}

    for course_data in course_jsons:
        course_code = course_data.get("course_code")

        if not course_code:
            continue

        course_code = course_code.replace(" ", "").upper()

        for topic in course_data.get("topics", []):
            normalized_topic = normalize_topic(topic)

            if normalized_topic not in topic_to_courses:
                topic_to_courses[normalized_topic] = set()

            topic_to_courses[normalized_topic].add(course_code)

    return topic_to_courses


def build_career_triples(
    careers: List[Dict[str, Any]],
    topic_to_courses: Dict[str, Set[str]]
) -> List[Dict[str, str]]:
    triples = []

    for career_data in careers:
        career = career_data.get("career")

        if not career:
            continue

        career = career.strip()

        for topic in career_data.get("topics", []):
            normalized_topic = normalize_topic(topic)

            triples.append({
                "subject": career,
                "relation": "REQUIRES_TOPIC",
                "object": normalized_topic,
                "subject_type": "Career",
                "object_type": "Topic"
            })

            matching_courses = topic_to_courses.get(normalized_topic, set())

            for course in matching_courses:
                triples.append({
                    "subject": normalized_topic,
                    "relation": "TAUGHT_IN",
                    "object": course,
                    "subject_type": "Topic",
                    "object_type": "Course"
                })

                triples.append({
                    "subject": career,
                    "relation": "RECOMMENDED_COURSE",
                    "object": course,
                    "subject_type": "Career",
                    "object_type": "Course"
                })

    return triples


def save_linked_triples(
    triples: List[Dict[str, str]],
    output_path: str
) -> None:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(triples, file, indent=4, ensure_ascii=False)

    print(f"Saved linked triples: {output_path}")