import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

def ask_llama(query, model="llama3-8b-8192"):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": (
                    "You are a helpful assistant speaking to a human through a voice interface. "
                    "Respond in short, simple, and natural sentences. Avoid long or complex answers. "
                    "Do not include any code or markdown. Be friendly and clear. "
                    "Your response will be translated and spoken aloud, so keep it easy to pronounce."
                )},
                {"role": "user", "content": query}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("❌ LLM error:", e)
        return None
