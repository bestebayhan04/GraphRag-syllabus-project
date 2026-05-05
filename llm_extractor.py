import json
import re
import requests
from typing import Any, Dict


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.1"


def call_ollama(prompt: str) -> str:
    """
    Send a prompt to local Ollama model.
    """
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
        },
        timeout=300,
    )

    response.raise_for_status()
    return response.json()["response"]


def extract_json_from_response(response: str) -> Dict[str, Any]:
    """
    Extract JSON object from LLM response.
    """
    match = re.search(r"\{.*\}", response, re.DOTALL)

    if not match:
        raise ValueError("No JSON object found in LLM response.")

    return json.loads(match.group(0))


def extract_syllabus_with_llm(text: str, source_file: str) -> Dict[str, Any]:
    """
    Extract structured course information from syllabus text using LLM.
    """
    prompt = f"""
You are extracting structured information from a university course syllabus.

Return ONLY valid JSON. Do not add explanation.

JSON schema:
{{
  "source_file": "{source_file}",
  "course_code": "",
  "course_title": "",
  "prerequisites": [],
  "corequisites": [],
  "topics": [],
  "learning_outcomes": []
}}

Rules:
- course_code should be like CS310, MATH201, IF100.
- prerequisites and corequisites should contain course codes only.
- topics should be short normalized topic names.
- learning_outcomes should be a list of clear sentences.
- If something is missing, use empty string or empty list.

Text:
{text[:4000]}
"""

    response = call_ollama(prompt)
    data = extract_json_from_response(response)

    data["source_file"] = source_file
    return data