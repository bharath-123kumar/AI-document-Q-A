import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
print(f"Using API Key: {api_key[:10]}...{api_key[-5:] if len(api_key) > 5 else ''}")

try:
    genai.configure(api_key=api_key)
    print("Listing models:")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name} (supports generateContent)")
except Exception as e:
    print(f"Error listing models: {e}")
