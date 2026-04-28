from dotenv import load_dotenv
import os
load_dotenv()

# Check API key
key = os.getenv("GOOGLE_API_KEY")
if key and key != "your_key_here":
    print(f"✓ API key is configured (starts with: {key[:8]}...)")
else:
    print("✗ WARNING: API key NOT set! Edit .env file and add your Gemini API key.")
    print("  Get one free at: https://aistudio.google.com/apikey")

# Check model name
model = os.getenv("GEMINI_MODEL")
if model:
    print(f"✓ Model configured: {model}")
else:
    print("✗ WARNING: GEMINI_MODEL not set in .env! Using default: gemini-2.5-flash")
    print("  To change models, add GEMINI_MODEL=your-model-name to .env")
