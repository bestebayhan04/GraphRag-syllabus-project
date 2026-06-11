from typing import Any, Dict, List
from sentence_transformers import SentenceTransformer, util


model = SentenceTransformer("all-MiniLM-L6-v2")

def get_course_texts(course_data: Dict[str, Any]) -> List[str]:
    """Flattens all learning outcomes and topics from a syllabus into a single list."""
    texts = []
    texts.extend(course_data.get("topics", []))
    texts.extend(course_data.get("learning_outcomes", []))
    return texts

def get_best_match_score(
    skill_embedding: Any,
    course_data: Dict[str, Any],
) -> float:
    """Returns the max similarity score between a skill and any text in a course syllabus."""
    texts = get_course_texts(course_data)
    if not texts:
        return 0.0
    text_embeddings = model.encode(texts, convert_to_tensor=True)
    similarities = util.cos_sim(skill_embedding, text_embeddings)[0]
    return float(similarities.max())


def find_courses_for_skill(
    skill_title: str,
    course_jsons: List[Dict[str, Any]],
    similarity_threshold: float,
) -> List[str]:
    """Returns a list of course codes whose syllabus matches the skill above threshold."""
    skill_embedding = model.encode(skill_title, convert_to_tensor=True)
    course_list = []
    for course_data in course_jsons:
        course_code = course_data.get("course_code", "").replace(" ", "").upper()
        if not course_code:
            continue
        score = get_best_match_score(skill_embedding, course_data)
        if score >= similarity_threshold:
            course_list.append(course_code)
    return course_list


def build_skill_course_map(
    skills: List[Dict[str, Any]],
    course_jsons: List[Dict[str, Any]],
    similarity_threshold: float,
) -> Dict[str, Dict]:
    """Builds {skill_id: {"title": ..., "courses": [course_codes]}} dict."""
    return {
        skill["id"]: {
            "title": skill["title"],
            "courses": find_courses_for_skill(skill["title"], course_jsons, similarity_threshold)
        }
        for skill in skills
    }


def build_career_course_links(
    careers: List[Dict[str, Any]],
    course_jsons: List[Dict[str, Any]],
    similarity_threshold: float = 0.5,
) -> List[Dict[str, Any]]:
    """Builds a list of career-skill-course linkages using semantic similarity."""
    results = []
    for career_data in careers:
        career_id = career_data.get("id", "")
        career = career_data.get("mainLabel", "").strip()
        skills = career_data.get("skills", [])
        if not career or not skills:
            continue
        skill_course_map = build_skill_course_map(skills, course_jsons, similarity_threshold)
        results.append({
            "career_id": career_id,
            "career": career,
            "skill_course_map": skill_course_map
        })
    return results