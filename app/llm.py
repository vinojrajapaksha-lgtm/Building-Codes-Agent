import os
from typing import List, Tuple

import requests

OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"


def build_prompt(question: str, context_chunks: List[Tuple[int, str, str]]) -> str:
    if not context_chunks:
        return (
            "You are a research assistant. No documents matched the query. "
            "Explain that no relevant PDFs were found and suggest uploading more PDFs."
        )

    context_text = "\n\n".join(
        f"Document {doc_id} ({filename}): {snippet}"
        for doc_id, filename, snippet in context_chunks
    )
    return (
        "You are a research assistant. Answer the question using the provided context. "
        "If the context is insufficient, say so and recommend next steps.\n\n"
        f"Context:\n{context_text}\n\nQuestion: {question}"
    )


def generate_answer(question: str, context_chunks: List[Tuple[int, str, str]]) -> str:
    api_key = os.environ.get("OPENAI_API_KEY")
    prompt = build_prompt(question, context_chunks)
    if not api_key:
        return (
            "No OpenAI API key configured. Here is the relevant context you can use: \n\n"
            + prompt
        )

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are a helpful research assistant."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    response = requests.post(OPENAI_API_URL, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]
