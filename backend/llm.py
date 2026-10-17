import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

ANSWER_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
HELPER_MODEL = os.getenv("GEMINI_HELPER_MODEL", "gemini-3.1-flash-lite-preview")


def generate_answer(prompt, system=None, model=ANSWER_MODEL, max_tokens=2048):
    config = {"max_output_tokens": max_tokens, "temperature": 0.2}

    if system:
        config["system_instruction"] = system

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=config,
    )

    return (response.text or "").strip()


def generate_helper(prompt):
    return generate_answer(prompt, model=HELPER_MODEL, max_tokens=1024)