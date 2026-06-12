import json
import random

def generate_data():
    data = {"nodes": {"courses": [], "occupations": [], "skills": []}, "edges": []}
    
    # 1. Generate Courses with "levels" to prevent cycles
    # Courses with lower levels are "early" courses, higher levels are "advanced"
    course_data = []
    for i in range(1, 21):
        level = (i // 5) + 1  # Courses are grouped into levels 1-4
        code = f"CS{100+i}"
        course_data.append({"code": code, "level": level})
        data["nodes"]["courses"].append({
            "course code": code, 
            "course title": f"Title {code}", 
            "source file": "f.pdf", 
            "topics": [], 
            "learning outcomes": []
        })

    # Generate other nodes
    for i in range(1, 11):
        data["nodes"]["occupations"].append({"id": f"OCC_{i}", "title": f"Occupation {i}", "alternative titles": [], "description": ""})
    for i in range(1, 21):
        data["nodes"]["skills"].append({"id": f"SK_{i}", "title": f"Skill {i}"})
        
    # 2. Generate Edges with cycle prevention
    # Rules: PREREQ/COREQ only point from higher level to lower level
    for _ in range(60):
        src = random.choice(course_data)
        tgt = random.choice(course_data)
        
        # Only allow PREREQ/COREQ if target level < source level
        # This guarantees A -> B where B is "earlier" than A
        if tgt['level'] < src['level']:
            rel = random.choice(["PREREQ", "COREQ"])
            data["edges"].append([src['code'], tgt['code'], rel])
            
    # Add other relationships (no cycles possible since they don't loop back)
    for _ in range(20):
        data["edges"].append([random.choice(course_data)['code'], f"SK_{random.randint(1,20)}", "COVERS"])
    for _ in range(20):
        data["edges"].append([f"OCC_{random.randint(1,10)}", f"SK_{random.randint(1,20)}", "REQUIRES"])
            
    with open("test_dataset.json", "w") as f:
        json.dump(data, f, indent=2)

generate_data()