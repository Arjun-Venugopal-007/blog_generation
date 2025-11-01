import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    # OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    # HF_API_TOKEN = os.getenv("HF_API_TOKEN")
    # REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")  
    # DEEPAI_API_KEY = os.getenv("DEEPAI_API_KEY")
    CLIENT_ID = os.getenv("OPENVERSE_CLIENT_ID")
    CLIENT_SECRET = os.getenv("OPENVERSE_CLIENT_SECRET")
    # Optional strict checks depending on what you're using
    # if not HF_API_TOKEN:
    #     raise ValueError("HF_API_TOKEN is missing in .env for Hugging Face image generation.")
