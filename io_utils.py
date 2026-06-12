import json
import os
from typing import Any, Dict, List

def convert_to_triples(
    results: List[Dict[str, Any]],
    course_jsons: List[Dict[str, Any]],
) -> List[Dict[str, str]]:
    """
    Converts build_career_course_links output into knowledge graph triples.

    Triple types:
      career_id  -[REQUIRES]->  skill_id
      course_id  -[COVERS]->    skill_id
      course_id  -[PREREQ]->    course_id
    """
    triples = []
    seen = set()  # deduplicate

    def add(subject, relation, object_, subject_type, object_type):
        key = (subject, relation, object_)
        if key not in seen:
            seen.add(key)
            triples.append({
                "subject":      subject,
                "relation":     relation,
                "object":       object_,
                "subject_type": subject_type,
                "object_type":  object_type,
            })

    # --- REQUIRES and COVERS triples (from linker output) ---
    for result in results:
        career_id       = result["career_id"]
        skill_course_map = result["skill_course_map"]  # {skill_id: {"title": ..., "courses": [...]}}

        for skill_id, skill_data in skill_course_map.items():
            # career -[REQUIRES]-> skill
            add(career_id, "REQUIRES", skill_id, "Career", "Skill")

            # course -[COVERS]-> skill
            for course_code in skill_data["courses"]:
                add(course_code, "COVERS", skill_id, "Course", "Skill")

    # --- PREREQ triples (from raw course data) ---
    for course in course_jsons:
        course_code = course.get("course_code", "")
        if not course_code:
            continue
        for prereq in course.get("prerequisites", []):
            add(course_code, "PREREQ", prereq, "Course", "Course")

    return triples