import pulp
from neo4j import GraphDatabase
import graphlib


def get_relevant_curriculum(minimal_set, edges):
    # 'edges' is a list of {'from': ..., 'to': ..., 'type': ...}
    
    relevant_list = set(minimal_set)
    changed = True

    while changed:
        changed = False
        for edge in edges:
            u, v, t = edge['from'], edge['to'], edge['type']
            
            # Rule (i) & (ii): Add neighbors based on constraints
            if t == 'PREREQ':
                # If v is in LIST, then u (the prereq) must be in LIST
                if v in relevant_list and u not in relevant_list:
                    relevant_list.add(u)
                    changed = True
            
            elif t == 'COREQ':
                # Rule (ii): If either is in LIST, add the other
                if u in relevant_list and v not in relevant_list:
                    relevant_list.add(v)
                    changed = True
                elif v in relevant_list and u not in relevant_list:
                    relevant_list.add(u)
                    changed = True
                    
        # Rule (iii) is satisfied automatically because we never
        # add a node based on an emanating PREREQ edge (u -> v where u is in LIST).
        
    return list(relevant_list)


def get_ordered_curriculum(minimal_set, uri, auth):
    driver = GraphDatabase.driver(uri, auth=auth)
    
    # The Cypher query returns the codes and the relationship map
    query = """
    MATCH (start:Course)
    WHERE start.id IN $minimal_courses
    MATCH (pre:Course)-[:PREREQ|COREQ*0..]-(start)
    WITH collect(DISTINCT pre) AS all_nodes

    UNWIND all_nodes AS n
    MATCH (n)-[r:PREREQ|COREQ]-(m:Course)
    WHERE m IN all_nodes
    RETURN [node in all_nodes | node.id] AS course_codes,
        collect(DISTINCT {from: startNode(r).id, to: endNode(r).id, type: type(r)}) AS edges
    """
    
    with driver.session() as session:
        result = session.run(query, minimal_courses=minimal_set).data()[0]

        relevant_list = get_relevant_curriculum(minimal_set, result["edges"])

        if not result:
            return []
            
        course_codes = result['course_codes']
        raw_edges = result['edges']

    final_edges = [e for e in raw_edges if e['from'] in relevant_list and e['to'] in relevant_list]

    graph = {code: set() for code in relevant_list}
    for e in final_edges:
        graph[e['to']].add(e['from'])

    # Perform Topological Sort
    try:
        ts = graphlib.TopologicalSorter(graph)
        ordered_list = list(ts.static_order())
        return ordered_list
    except graphlib.CycleError:
        return "Error: Circular dependency detected in your course requirements."


def solve_min_courses_by_course(title, uri, auth):
    driver = GraphDatabase.driver(uri, auth=auth)
    
    # 1. Fetch data: For each course, what skills does it cover that are required by the occupation?
    query = """
    MATCH (occ:Occupation {title: $occ_title})-[:REQUIRES]->(s:Skill)
    MATCH (c:Course)-[:COVERS]->(s)
    RETURN c.id AS course, collect(s.id) AS covered_skills
    """
    
    with driver.session() as session:
        results = session.run(query, occ_title=title).data()
    
    # 2. Extract the Universe (all skills required by the occupation)
    required_skills_query = """
    MATCH (occ:Occupation {title: $occ_title})-[:REQUIRES]->(s:Skill)
    WHERE EXISTS {
        MATCH (:Course)-[:COVERS]->(s)
    }
    RETURN collect(s.id) AS skills
    """
    with driver.session() as session:
        required_skills = session.run(required_skills_query, occ_title=title).single()['skills']

    # 3. Model as Set Cover
    course_data = {r["course"]: set(r["covered_skills"]) for r in results}
    all_courses = list(course_data.keys())
    
    prob = pulp.LpProblem("SetCover", pulp.LpMinimize)
    course_vars = pulp.LpVariable.dicts("Course", all_courses, cat=pulp.LpBinary)
    
    # Objective: Minimize number of courses
    prob += pulp.lpSum([course_vars[c] for c in all_courses])
    
    # Constraints: For each required skill, at least one selected course must contain it
    for skill in required_skills:
        prob += pulp.lpSum([course_vars[c] for c in all_courses if skill in course_data[c]]) >= 1
        
    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    return [c for c in all_courses if course_vars[c].value() == 1]



if __name__ == "__main__":

    auth = ("neo4j", "kg_project")
    uri = "bolt://localhost:7687"

    while True:
        occ = input("Provide an occupation: ")

        if occ == "q":
            break

        # PLACEHOLDER: find the most similar title
        title = occ

        # find the minimum number of courses covering the skills
        selected_courses = solve_min_courses_by_course(title, uri, auth)

        ordered_curriculum = get_ordered_curriculum(selected_courses, uri, auth)

        print("Recommended Curriculum:", ordered_curriculum)