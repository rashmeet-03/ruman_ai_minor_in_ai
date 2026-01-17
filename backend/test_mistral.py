"""
Quick test script to check if Mistral API is working
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.getenv("MISTRAL_API_KEY")

print("=" * 50)
print("🔍 Mistral API Key Test")
print("=" * 50)

if not api_key:
    print("❌ ERROR: MISTRAL_API_KEY not found in .env file!")
    print("\nTo get a Mistral API key:")
    print("1. Go to https://console.mistral.ai/")
    print("2. Create an account")
    print("3. Go to API Keys section")
    print("4. Create a new API key")
    print("5. Add to .env: MISTRAL_API_KEY=your_key_here")
    exit(1)

print(f"✅ API Key found: {api_key[:8]}...{api_key[-4:]}")
print(f"   Length: {len(api_key)} characters")

print("\n📦 Installing/Checking mistralai package...")

try:
    from mistralai import Mistral
    print("✅ mistralai package is installed")
except ImportError:
    print("❌ mistralai package not installed")
    print("   Run: pip install mistralai")
    exit(1)

print("\n🧪 Testing API connection...")

try:
    client = Mistral(api_key=api_key)
    
    # List available models
    print("\n📋 Available models:")
    models = client.models.list()
    for model in models.data[:10]:  # Show first 10
        print(f"   - {model.id}")
    
    # Test generation
    print("\n🧪 Testing content generation...")
    
    response = client.chat.complete(
        model="mistral-small-latest",
        messages=[
            {"role": "user", "content": "Say 'Hello! Mistral API is working!' in exactly those words."}
        ]
    )
    
    print("\n✅ SUCCESS! Mistral API is working!")
    print(f"\n📝 Response: {response.choices[0].message.content}")
    
except Exception as e:
    print(f"\n❌ ERROR: API call failed!")
    print(f"   Error type: {type(e).__name__}")
    print(f"   Error message: {str(e)}")
    
    if "401" in str(e) or "Unauthorized" in str(e):
        print("\n💡 Your API key appears to be invalid. Please check:")
        print("   1. Go to https://console.mistral.ai/")
        print("   2. Create a new API key")
        print("   3. Update MISTRAL_API_KEY in your .env file")
    elif "quota" in str(e).lower() or "limit" in str(e).lower():
        print("\n💡 You may have exceeded your API quota or rate limit.")

print("\n" + "=" * 50)
