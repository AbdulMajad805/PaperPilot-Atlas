
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
    raise ValueError("GROQ_API_KEY is missing. Please configure it in your .env file.")

analyst_llm = ChatGroq(
    model=GROQ_MODEL,
    temperature=0.1,
    max_tokens=4096,
    api_key=GROQ_API_KEY,
)

reviewer_llm = ChatGroq(
    model=GROQ_MODEL,
    temperature=0.1,
    max_tokens=4096,
    api_key=GROQ_API_KEY,
)
