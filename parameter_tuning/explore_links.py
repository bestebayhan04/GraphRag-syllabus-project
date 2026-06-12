from pathlib import Path
import sys
import json
import random

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from read_data import read_career_files, read_course_file, download_all
from linker import get_best_match_score
from embeddings import model

THRESHOLD = 0.45
OUTPUT_PATH = Path(__file__).parent / "exploration_results.json"


def build_exploration_map(careers, courses, threshold):
    # collect all unique skills across all careers
    all_skills = {}
    for career in careers:
        for skill in career.get("skills", []):
            all_skills[skill["id"]] = skill["title"]

    # precompute embeddings for all skills once
    skill_ids = list(all_skills.keys())
    skill_titles = [all_skills[sid] for sid in skill_ids]
    skill_embeddings = {
        sid: model.encode(title, convert_to_tensor=True)
        for sid, title in zip(skill_ids, skill_titles)
    }

    exploration_map = {}

    for course in courses:
        course_code = course.get("course_code", "")
        if not course_code:
            continue

        matched = []
        unmatched = {}

        for sid, embedding in skill_embeddings.items():
            score = get_best_match_score(embedding, course)
            if score >= threshold:
                matched.append({sid: all_skills[sid]})
            else:
                unmatched[sid] = all_skills[sid]
        
        print("matched",len(matched), "unmatched", len(unmatched))

        n_soft = max(1, len(matched) // 2)
        soft_neg_ids = random.sample(list(unmatched.keys()), min(n_soft, len(unmatched)))
        soft_negatives = [{neg_id: unmatched[neg_id]} for neg_id in soft_neg_ids]

        exploration_map[course_code] = {
            "candidates": matched,
            "soft_negative_candidates": soft_negatives
        }
    return exploration_map

def save_exploration_map(exploration_map, output_path=OUTPUT_PATH):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(exploration_map, f, indent=2)
    print(f"Saved exploration results to {output_path}")


if __name__ == "__main__":
    download_all()
    careers = read_career_files()
    courses = read_course_file()
    exploration_map = build_exploration_map(careers, courses, THRESHOLD)
    save_exploration_map(exploration_map)