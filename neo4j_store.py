import json
import os
from typing import Dict, List

from neo4j import GraphDatabase


NEO4J_URI = "bolt://localhost:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "password123"

TRIPLES_FOLDER = "outputs/triples"


def load_all_triples(folder_path: str) -> List[Dict[str, str]]:
    triples = []

    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            path = os.path.join(folder_path, filename)

            with open(path, "r", encoding="utf-8") as file:
                data = json.load(file)

                if isinstance(data, list):
                    triples.extend(data)

    return triples


def safe_label(label: str) -> str:
    allowed = {"Course", "Topic", "Career"}

    if label in allowed:
        return label

    return "Entity"


def safe_relation(relation: str) -> str:
    return relation.upper().replace(" ", "_").replace("-", "_")


def clear_database(driver) -> None:
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")

    print("Cleared Neo4j database.")


def create_relationship(tx, triple: Dict[str, str]) -> None:
    subject = triple["subject"]
    object_ = triple["object"]

    relation = safe_relation(triple["relation"])
    subject_label = safe_label(triple.get("subject_type", "Entity"))
    object_label = safe_label(triple.get("object_type", "Entity"))

    query = f"""
    MERGE (s:{subject_label} {{name: $subject}})
    MERGE (o:{object_label} {{name: $object}})
    MERGE (s)-[r:{relation}]->(o)
    """

    tx.run(query, subject=subject, object=object_)


def insert_triples(
    triples: List[Dict[str, str]],
    clear_first: bool = True
) -> None:
    driver = GraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USERNAME, NEO4J_PASSWORD),
    )

    try:
        if clear_first:
            clear_database(driver)

        with driver.session() as session:
            for triple in triples:
                session.execute_write(create_relationship, triple)

        print(f"Inserted {len(triples)} triples into Neo4j.")

    finally:
        driver.close()


def main() -> None:
    triples = load_all_triples(TRIPLES_FOLDER)
    print(f"Loaded triples: {len(triples)}")

    insert_triples(triples, clear_first=True)


if __name__ == "__main__":
    main()