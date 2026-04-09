import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

MODEL_NAME = "groq/llama-3.1-8b-instant"

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY missing from .env")
if not SERPER_API_KEY:
    raise ValueError("SERPER_API_KEY missing from .env")