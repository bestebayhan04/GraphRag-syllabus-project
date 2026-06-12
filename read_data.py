import os
import json
import gdown
from pathlib import Path

CAREER_FOLDER_ID = "1ZV4tmZZcuKZ_prQJTIcYXyKTnrTgir_3"
COURSE_FILE_ID = "1rjBi0iNx9tzXgRvJDOyC5cxpFxt25jG8"

BASE_DIR = Path(__file__).resolve().parent

CAREER_DATA_DIR = BASE_DIR / "data" / "careers"
COURSE_FILE_PATH = BASE_DIR / "data" / "courses" / "scripts.json"


def download_folder(folder_id: str, output_dir: str):
    if not os.path.exists(output_dir) or not os.listdir(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        url = f"https://drive.google.com/drive/folders/{folder_id}"
        gdown.download_folder(url, output=output_dir, quiet=False, use_cookies=False)
    else:
        print(f"Data already exists at {output_dir}, skipping download.")


def download_file(file_id: str, output_path: str):
    if not os.path.exists(output_path):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        url = f"https://drive.google.com/uc?id={file_id}"
        gdown.download(url, output_path, quiet=False)
    else:
        print(f"File already exists at {output_path}, skipping download.")


def download_all():
    download_folder(CAREER_FOLDER_ID, CAREER_DATA_DIR)
    download_file(COURSE_FILE_ID, COURSE_FILE_PATH)


def read_career_files(data_dir: str = CAREER_DATA_DIR) -> list[dict]:
    careers = []
    for filename in os.listdir(data_dir):
        if filename.endswith(".json"):
            filepath = os.path.join(data_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                careers.append(json.load(f))
    return careers


def read_course_file(filepath: str = COURSE_FILE_PATH) -> list[dict]:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read().strip()
    if not content.startswith("["):
        content = f"[{content}]"
    return json.loads(content)
