from transformers import pipeline

MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"

generator = pipeline(
    "text-generation",
    model=MODEL_NAME,
)

# Set generation settings once, on the model's config
gen_config = generator.model.generation_config
gen_config.max_new_tokens = 200
gen_config.max_length = None  # fixes the "max_length=20" issue
gen_config.do_sample = False


def generate_answer(prompt: str) -> str:
    messages = [{"role": "user", "content": prompt}]

    result = generator(
        messages,
        return_full_text=False,  # only new generated text
    )

    return result[0]["generated_text"].strip()
