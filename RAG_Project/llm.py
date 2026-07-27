"""
Calls an LLM (Gemini or OpenAI) with retrieved context + the user question.
"""

from config import (
    LLM_PROVIDER,
    GEMINI_API_KEY,
    OPENAI_API_KEY,
    GEMINI_MODEL,
    OPENAI_MODEL,
)


def _build_prompt(question: str, context_chunks: list[str]) -> str:
    """Combine retrieved chunks and the user question into one prompt."""
    context = "\n\n---\n\n".join(context_chunks)

    return f"""You are a helpful assistant answering questions about an uploaded PDF.

Use the CONTEXT below as your main source.
- If the answer is clearly in the context, answer directly and clearly.
- If the context only partially covers the question, answer from what is available and briefly note what is missing.
- Only say you could not find the information if the context is truly unrelated to the question.
- Do not invent facts that are not supported by the context.

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:"""


def _call_gemini(prompt: str) -> str:
    """Send the prompt to Google Gemini and return the answer text."""
    if not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY is not set. "
            "Add it in config.py or set the GEMINI_API_KEY environment variable."
        )

    import google.generativeai as genai

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(GEMINI_MODEL)
    response = model.generate_content(prompt)
    return response.text.strip()


def _call_openai(prompt: str) -> str:
    """Send the prompt to OpenAI and return the answer text."""
    if not OPENAI_API_KEY:
        raise ValueError(
            "OPENAI_API_KEY is not set. "
            "Add it in config.py or set the OPENAI_API_KEY environment variable."
        )

    from openai import OpenAI

    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You answer questions using the given PDF context. "
                    "Prefer answering from partial context over refusing."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()


def generate_answer(question: str, context_chunks: list[str]) -> str:
    """
    Ask the configured LLM to answer using the retrieved chunks.

    Args:
        question: User's question.
        context_chunks: Relevant text chunks from the vector DB.

    Returns:
        LLM-generated answer string.
    """
    if not context_chunks:
        return "No relevant information found. Please upload and process a PDF first."

    prompt = _build_prompt(question, context_chunks)

    provider = LLM_PROVIDER.lower().strip()

    if provider == "gemini":
        return _call_gemini(prompt)
    elif provider == "openai":
        return _call_openai(prompt)
    else:
        raise ValueError(
            f"Unknown LLM_PROVIDER '{LLM_PROVIDER}'. Use 'gemini' or 'openai'."
        )
