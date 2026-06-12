from pathlib import Path
import sys
import json

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))
config_path = PROJECT_ROOT / "config.json"

from explore_links import build_exploration_map, save_exploration_map
from label_with_llm import  label_main
from tune_threshold import load_tuning_data, precompute_course_embeddings, compute_scores, tune_threshold
from read_data import download_all, read_career_files, read_course_file

if __name__ == "__main__":
    download_all()
    careers = read_career_files()
    courses = read_course_file()
    course_index = {c["course_code"]: c for c in courses}

    # Step 1: build exploration map
    print("=== Step 1: Exploring links ===")
    exploration_map = build_exploration_map(careers, courses, threshold=0.4)
    save_exploration_map(exploration_map)

    # Step 2: label with LLM
    print("\n=== Step 2: Labeling with LLM ===")
    label_main()

    # Step 3: tune threshold
    print("\n=== Step 3: Tuning threshold ===")
    tuning_data = load_tuning_data()
    course_embeddings = precompute_course_embeddings(course_index)
    scored_data = compute_scores(tuning_data, course_embeddings)
    best_threshold = tune_threshold(scored_data)

    print(f"\nFinal best threshold: {best_threshold:.4f}")

    config = {"similarity_threshold": best_threshold}
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    print(f"Saved best threshold to {config_path}")