from typing import List

from neo4j import GraphDatabase


NEO4J_URI = "bolt://localhost:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "password123"


def run_query(query: str, params: dict | None = None) -> List[dict]:
    driver = GraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USERNAME, NEO4J_PASSWORD),
    )

    try:
        with driver.session() as session:
            result = session.run(query, params or {})
            return [record.data() for record in result]
    finally:
        driver.close()


def recommend_courses_for_career(career_name: str) -> List[str]:
    query = """
    MATCH (c:Career {name: $career})-[:REQUIRES_TOPIC]->(career_topic:Topic)
    MATCH (course:Course)-[:HAS_TOPIC]->(course_topic:Topic)
    WHERE toLower(course_topic.name) CONTAINS toLower(career_topic.name)
       OR toLower(career_topic.name) CONTAINS toLower(course_topic.name)
    RETURN DISTINCT course.name AS course
    ORDER BY course
    """

    rows = run_query(query, {"career": career_name})
    return [row["course"] for row in rows]

def get_topics_for_course(course_code: str) -> List[str]:
    query = """
    MATCH (course:Course {name: $course})-[:HAS_TOPIC]->(topic:Topic)
    RETURN DISTINCT topic.name AS topic
    ORDER BY topic
    """

    rows = run_query(query, {"course": course_code.upper()})
    return [row["topic"] for row in rows]


def get_prerequisites(course_code: str) -> List[str]:
    query = """
    MATCH (course:Course {name: $course})-[:HAS_PREREQ]->(prereq:Course)
    RETURN DISTINCT prereq.name AS prerequisite
    ORDER BY prerequisite
    """

    rows = run_query(query, {"course": course_code.upper()})
    return [row["prerequisite"] for row in rows]


def answer_question(question: str) -> str:
    q = question.lower()

    if "data scientist" in q:
        courses = recommend_courses_for_career("Data Scientist")
        return f"Recommended courses for Data Scientist: {', '.join(courses)}"

    if "machine learning engineer" in q:
        courses = recommend_courses_for_career("Machine Learning Engineer")
        return f"Recommended courses for Machine Learning Engineer: {', '.join(courses)}"

    if "cybersecurity analyst" in q:
        courses = recommend_courses_for_career("Cybersecurity Analyst")
        return f"Recommended courses for Cybersecurity Analyst: {', '.join(courses)}"

    if "data engineer" in q:
        courses = recommend_courses_for_career("Data Engineer")
        return f"Recommended courses for Data Engineer: {', '.join(courses)}"

    if "prerequisite" in q or "prereq" in q:
        words = question.replace("?", "").split()
        course_codes = [w.upper() for w in words if any(ch.isdigit() for ch in w)]

        if course_codes:
            prereqs = get_prerequisites(course_codes[0])
            return f"Prerequisites of {course_codes[0]}: {', '.join(prereqs)}"

    if "topic" in q or "topics" in q:
        words = question.replace("?", "").split()
        course_codes = [w.upper() for w in words if any(ch.isdigit() for ch in w)]

        if course_codes:
            topics = get_topics_for_course(course_codes[0])
            return f"Topics of {course_codes[0]}: {', '.join(topics)}"

    return "I could not map this question to a graph query yet."