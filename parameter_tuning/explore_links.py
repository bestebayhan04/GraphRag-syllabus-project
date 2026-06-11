import sys
sys.path.append("..")
from read_data import read_career_files, read_course_file, download_all
from linker import find_courses_for_skill
from random import choice

download_all()
careers = read_career_files() 
courses = read_course_file()

target_course = None
THRESHOLD = None 

matched = []
unmatched = []

for career in careers:
    for skill in career.get("skills", []):
        result = find_courses_for_skill(skill["title"], courses, THRESHOLD)
        if target_course in result:
            matched.append(skill)
        else:
            unmatched.append(skill)

print("=== MATCHED (positive/hard negative candidates) ===")
for s in matched:
    print(f"  {s['id']} | {s['title']}")

soft_negative = choice(unmatched) if unmatched else None
if soft_negative:
    print(f"SOFT NEGATIVE: {soft_negative['id']} | {soft_negative['title']}")