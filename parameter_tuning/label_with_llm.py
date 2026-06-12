from pathlib import Path
import sys
import json
import random

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

from openai import OpenAI
from read_data import read_course_file

EXPLORATION_PATH = Path(__file__).parent / "exploration_results.json"
COURSES_PATH = PROJECT_ROOT / "data" / "courses" / "scripts_.json"
OUTPUT_PATH = Path(__file__).parent / "tuning_dataset.jsonl"

client = OpenAI()


def load_exploration_results(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def sample_soft_negatives(soft_negatives, n_candidates):
    n_soft = max(1, n_candidates // 2)
    return random.sample(soft_negatives, min(n_soft, len(soft_negatives)))


def build_prompt(course_data, candidates, soft_negatives):
    topics = "\n".join(f"  - {t}" for t in course_data.get("topics", []))
    outcomes = "\n".join(f"  - {o}" for o in course_data.get("learning_outcomes", []))
    candidates_str = "\n".join(
        f"  - {list(c.keys())[0]}: {list(c.values())[0]}" for c in candidates
    )
    soft_neg_str = "\n".join(
        f"  - {list(s.keys())[0]}: {list(s.values())[0]}" for s in soft_negatives
    )

    return f"""Below are the topics and learning outcomes of a computer science university course.

Topics taught:
{topics}

Learning outcomes:
{outcomes}

Candidate skills (may or may not be taught in this course):
{candidates_str}

Soft negative pool (clearly unrelated skills, pick the best one):
{soft_neg_str}

From the candidate skills list, identify:
1. ONE positive: the skill most clearly and directly taught in this course. If no suitable positive exists, return null for this field.
2. ONE hard negative: a skill from the candidates that sounds technically related but is NOT actually taught in this course. If no suitable hard negative exists, return null for this field.

From the soft negative pool, identify:
3. ONE soft negative: the most clearly unrelated skill. If no unrelated skill exists, return null for this field.

All three selected skills must be distinct.
Each skill is listed as "id: title". Return the exact id and title from the lists above.
Respond only in JSON with no extra text:
{{"positive": {{"id": "...", "title": "..."}}, "hard_negative": {{"id": "...", "title": "..."}}, "soft_negative": {{"id": "...", "title": "..."}}}}"""


def label_course(course_data, candidates, soft_negatives):
    prompt = build_prompt(course_data, candidates, soft_negatives)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        max_tokens=256
    )
    raw = response.choices[0].message.content.strip()
    return json.loads(raw)


def label_main():
    courses = read_course_file()
    course_index = {c["course_code"]: c for c in courses}
    exploration_map = load_exploration_results(EXPLORATION_PATH)

    entries = []

    for course_code, data in exploration_map.items():
        candidates = data.get("candidates", [])
        soft_negatives = data.get("soft_negative_candidates", [])

        if len(candidates) < 2:
            print(f"Skipping {course_code} — not enough candidates for positive and hard negative.")
            continue

        if not soft_negatives:
            print(f"Skipping {course_code} — no soft negatives.")
            continue

        course_data = course_index.get(course_code)
        if not course_data:
            print(f"Skipping {course_code} — not found in courses file.")
            continue

        sampled_soft_negatives = sample_soft_negatives(soft_negatives, len(candidates))

        print(f"Labeling {course_code} ({len(candidates)} candidates, {len(sampled_soft_negatives)} soft negative candidates)...")
        try:
            result = label_course(course_data, candidates, sampled_soft_negatives)
            if result["positive"] is None:
                print(f"  Warning: no positive found for {course_code}")
            else:
                entries.append({
                    "skill_id": result["positive"]["id"],
                    "skill_title": result["positive"]["title"],
                    "course_code": course_code,
                    "label": 1
                })
            if result["hard_negative"] is not None:
                entries.append({
                    "skill_id": result["hard_negative"]["id"],
                    "skill_title": result["hard_negative"]["title"],
                    "course_code": course_code,
                    "label": 0
                })
            if result["soft_negative"] is not None:
                entries.append({
                    "skill_id": result["soft_negative"]["id"],
                    "skill_title": result["soft_negative"]["title"],
                    "course_code": course_code,
                    "label": 0
                })

        except Exception as e:
            print(f"  Failed for {course_code}: {e}")
            continue

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")

    print(f"\nDone. {len(entries)} entries saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    label_main()