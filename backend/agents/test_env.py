import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if api_key:
    print(f"✅ API Key found: {api_key[:10]}...{api_key[-5:]}")
    print(f"   Length: {len(api_key)} characters")
else:
    print("❌ No API key found!")
    print("   Make sure .env file exists in project root")