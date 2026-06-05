import time
from google import genai
from app.core.config import settings

client = genai.Client(api_key=settings.gemini_api_key)


def generate_answer(prompt: str) -> str:
    models = [
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite"
    ]

    last_error = None

    for model_name in models:
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )

                if response.text:
                    return response.text

            except Exception as e:
                last_error = e
                print(
                    f"Gemini error with {model_name}, "
                    f"attempt {attempt + 1}: {e}"
                )
                time.sleep(2)

    return f"LLM service temporarily unavailable. Last error: {last_error}"