from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

try:
    response = client.chat.completions.create(
        # model="z-ai/glm-5.2:free",
        model="openai/gpt-5-nano",
        messages=[{"role": "user", "content": "Say hello"}],
        # max_tokens=1000
    )
    print(response.choices[0].message.content)
except Exception as e:
    print(f"OpenAI error: {e}")

    # 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