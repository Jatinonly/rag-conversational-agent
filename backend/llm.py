from transformers import pipeline

MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"

generator = pipeline(  # Create a text-generation system using this model.
    "text-generation",
    model=MODEL_NAME,
)


def generate_answer(prompt: str) -> str:
    messages = [
        {
            "role": "user",
            "content": prompt,
        }
    ]

    result = generator(
        messages,
        max_new_tokens=200,
        do_sample=False,
    )

    return result[0]["generated_text"][-1]["content"]
