import json
import torch
from pathlib import Path
from typing import Any, Dict
from sentence_transformers import util
from embeddings import model
from read_data import download_file, BASE_DIR

CAREER_LABELS_FILE_ID = "1fNzLErogljh4-p6IftUfhoLcJD6VCpL1"
CAREER_LABELS_PATH = BASE_DIR / "data" / "career_labels.json"
CAREER_EMBEDDINGS_PATH = BASE_DIR / "outputs" / "career_embeddings.pt"


def download_career_labels():
    download_file(CAREER_LABELS_FILE_ID, str(CAREER_LABELS_PATH))


def embed_and_save_careers(
    career_labels_path: Path = CAREER_LABELS_PATH,
    output_path: Path = CAREER_EMBEDDINGS_PATH,
) -> None:
    """Precomputes and saves embeddings for all career labels."""
    download_career_labels()

    with open(career_labels_path, "r", encoding="utf-8") as f:
        careers = json.load(f)

    career_ids = []
    labels = []

    for career in careers:
        all_labels = [career["mainLabel"]] + career["alternativeLabels"]
        for label in all_labels:
            career_ids.append(career["id"])
            labels.append(label)

    embeddings = model.encode(labels, convert_to_tensor=True)

    torch.save(
        {
            "career_ids": career_ids,
            "labels": labels,
            "embeddings": embeddings,
        },
        str(output_path),
    )
    print(f"Saved embeddings for {len(labels)} labels across {len(careers)} careers to {output_path}")


def find_best_career(
    query: str,
    embeddings_path: Path = CAREER_EMBEDDINGS_PATH,
) -> Dict[str, Any]:
    """Loads precomputed embeddings and returns the best matching career for a query."""
    data = torch.load(str(embeddings_path))
    career_ids = data["career_ids"]
    labels = data["labels"]
    embeddings = data["embeddings"]

    query_embedding = model.encode(query, convert_to_tensor=True)
    similarities = util.cos_sim(query_embedding, embeddings)[0]

    career_scores: Dict[str, float] = {}
    career_best_label: Dict[str, str] = {}

    for idx, (career_id, label) in enumerate(zip(career_ids, labels)):
        score = float(similarities[idx])
        if career_id not in career_scores or score > career_scores[career_id]:
            career_scores[career_id] = score
            career_best_label[career_id] = label

    best_career_id = max(career_scores, key=career_scores.get)

    return {
        "career_id": best_career_id,
        "score": career_scores[best_career_id],
        "matched_label": career_best_label[best_career_id],
    }