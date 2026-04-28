"""Quick test to see what Gemini models are available with your API key"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

print("Available Gemini models:")
print("=" * 60)

for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"✓ {model.name}")
        print(f"  Display name: {model.display_name}")
        print()

print("=" * 60)
print("\nTry using one of the model names above in your scripts.")
print("Remove the 'models/' prefix when using with LangChain.")
