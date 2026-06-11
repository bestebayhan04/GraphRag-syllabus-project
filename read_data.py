import os
import json
import gdown


CAREER_FOLDER_ID = "your_folder_id_here"
COURSE_FOLDER_ID = "your_folder_id_here"

CAREER_DATA_DIR = "data/careers"
COURSE_DATA_DIR = "data/courses"


def download_folder(folder_id: str, output_dir: str):
    if not os.path.exists(output_dir) or not os.listdir(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        url = f"https://drive.google.com/drive/folders/{folder_id}"
        gdown.download_folder(url, output=output_dir, quiet=False, use_cookies=False)
    else:
        print(f"Data already exists at {output_dir}, skipping download.")


def download_all():
    download_folder(CAREER_FOLDER_ID, CAREER_DATA_DIR)
    download_folder(COURSE_FOLDER_ID, COURSE_DATA_DIR)


def read_career_files(data_dir: str = CAREER_DATA_DIR) -> list[dict]:
    careers = []
    for filename in os.listdir(data_dir):
        if filename.endswith(".json"):
            filepath = os.path.join(data_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                careers.append(json.load(f))
    return careers


def read_course_files(data_dir: str = COURSE_DATA_DIR) -> list[dict]:
    courses = []
    for filename in os.listdir(data_dir):
        if filename.endswith(".json"):
            filepath = os.path.join(data_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                courses.append(json.load(f))
    return courses


if __name__ == "__main__":
    download_all()

    careers = read_career_files()
    print(f"Loaded {len(careers)} career entries.")

    courses = read_course_files()
    print(f"Loaded {len(courses)} course entries.")