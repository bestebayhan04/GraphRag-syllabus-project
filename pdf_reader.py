import os
from langchain_community.document_loaders import PyPDFLoader


def extract_pdf_text(file_path: str) -> str:
    """
    Extract text from a PDF file page by page.

    Args:
        file_path: Path to the PDF file.

    Returns:
        Extracted text as a single string.
    """
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    full_text = []

    for i, doc in enumerate(documents, start=1):
        page_text = f"\n--- Page {i} ---\n{doc.page_content}"
        full_text.append(page_text)

    return "\n".join(full_text)


def save_text_output(
    pdf_filename: str,
    text: str,
    output_dir: str = "outputs/texts"
) -> str:
    """
    Save extracted PDF text into a .txt file.
    """
    os.makedirs(output_dir, exist_ok=True)

    base_name = os.path.splitext(pdf_filename)[0]
    output_path = os.path.join(output_dir, f"{base_name}.txt")

    with open(output_path, "w", encoding="utf-8") as file:
        file.write(text)

    return output_path