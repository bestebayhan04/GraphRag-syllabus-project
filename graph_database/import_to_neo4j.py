import json
from neo4j import GraphDatabase

# Database connection details
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "kg_project")

def import_data(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)

    driver = GraphDatabase.driver(URI, auth=AUTH)

    with driver.session() as session:
        # 1. Create Nodes
        for course in data['nodes']['courses']:
            session.run("""
                MERGE (c:Course {id: $code})
                SET c.id=$code, c.title = $title, c.source = $source, 
                    c.topics = $topics, c.outcomes = $outcomes
            """, code=course['course code'], title=course['course title'], 
                 source=course['source file'], topics=course['topics'], 
                 outcomes=course['learning outcomes'])

        for occ in data['nodes']['occupations']:
            session.run("""
                MERGE (o:Occupation {id: $id})
                SET o.title = $title, o.description = $description, 
                    o.alt_titles = $alt_titles
            """, id=occ['id'], title=occ['title'], 
                 description=occ['description'], alt_titles=occ['alternative titles'])

        for skill in data['nodes']['skills']:
            session.run("MERGE (s:Skill {id: $id, title: $title})", 
                        id=skill['id'], title=skill['title'])

        # 2. Create Edges
        # Assumes edges list format: [from_id, to_id, type]
        for edge in data['edges']:
            source, target, rel_type = edge
            session.run(f"""
                MATCH (a {{id: $source}}) 
                MATCH (b {{id: $target}})
                MERGE (a)-[r:{rel_type.upper()}]->(b)
            """, source=source, target=target)

    driver.close()
    print("Import complete.")


import_data("test_dataset.json")