import os
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime

# Load API key from .env file
load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# Path to history file
HISTORY_FILE = "conversation_history.txt"

def log_conversation(user_input, bot_reply):
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"🕒 {datetime.now()}\n")
        f.write(f"👤 User: {user_input}\n")
        f.write(f"🤖 Bot: {bot_reply}\n\n")

def ask_llama(query, model="llama3-8b-8192"):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant speaking to a human through a voice interface. "
                        "Respond in short, simple, and natural sentences. Avoid long or complex answers. "
                        "Do not include any code or markdown. Be friendly and clear. "
                        "Your response will be translated and spoken aloud, so keep it easy to pronounce."
                    )
                },
                {"role": "user", "content": query}
            ]
        )
        reply = response.choices[0].message.content.strip()

        # Save conversation
        log_conversation(query, reply)

        return reply
    except Exception as e:
        print("❌ LLM error:", e)
        error_msg = "ಕ್ಷಮಿಸಿ, ಉತ್ತರ ನೀಡಲು ವಿಫಲವಾಗಿದೆ."
        log_conversation(query, error_msg)
        return error_msg
