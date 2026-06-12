import sys
import json
from sklearn.metrics import f1_score, precision_score, recall_score
from sentence_transformers import util
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from linker import get_course_texts
from embeddings import model

TUNING_DATA_PATH = Path(__file__).parent / "tuning_dataset.jsonl"


def load_tuning_data():
    data = []
    with open(TUNING_DATA_PATH, "r") as f:
        for line in f:
            data.append(json.loads(line))
    return data


def precompute_course_embeddings(course_index):
    return {
        code: model.encode(get_course_texts(course), convert_to_tensor=True)
        for code, course in course_index.items()
    }


def compute_scores(tuning_data, course_embeddings):
    results = []
    for entry in tuning_data:
        skill_embedding = model.encode(entry["skill_title"], convert_to_tensor=True)
        course_emb = course_embeddings[entry["course_code"]]
        score = float(util.cos_sim(skill_embedding, course_emb)[0].max())
        results.append({"score": score, "label": entry["label"]})
    return results


def tune_threshold(scored_data):
    candidate_thresholds = sorted(set(d["score"] for d in scored_data))
    best_f1 = 0
    best_threshold = 0
    rows = []

    for threshold in candidate_thresholds:
        y_true = [d["label"] for d in scored_data]
        y_pred = [1 if d["score"] >= threshold else 0 for d in scored_data]

        f1 = f1_score(y_true, y_pred, zero_division=0)
        precision = precision_score(y_true, y_pred, zero_division=0)
        recall = recall_score(y_true, y_pred, zero_division=0)
        rows.append((round(threshold, 4), precision, recall, f1))

        if f1 > best_f1:
            best_f1 = f1
            best_threshold = threshold

    print(f"{'Threshold':<12} {'Precision':<12} {'Recall':<12} {'F1':<12}")
    for row in rows:
        print(f"{row[0]:<12} {row[1]:<12.2f} {row[2]:<12.2f} {row[3]:<12.2f}")

    print(f"\nBest threshold: {best_threshold:.4f} with F1: {best_f1:.2f}")
    return best_threshold


if __name__ == "__main__":
    from read_data import download_all, read_course_file
    download_all()
    courses = read_course_file()
    course_index = {c["course_code"]: c for c in courses}
    tuning_data = load_tuning_data()
    course_embeddings = precompute_course_embeddings(course_index)
    scored_data = compute_scores(tuning_data, course_embeddings)
    best_threshold = tune_threshold(scored_data)