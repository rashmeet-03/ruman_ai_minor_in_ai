"""
Quick test script to check if Gemini API is working
Updated to try multiple model names
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

print("=" * 50)
print("🔍 Gemini API Key Test")
print("=" * 50)

if not api_key:
    print("❌ ERROR: GEMINI_API_KEY not found in .env file!")
    exit(1)

print(f"✅ API Key found: {api_key[:10]}...{api_key[-4:]}")

print("\n🧪 Testing available models...")

try:
    import google.generativeai as genai
    import warnings
    warnings.filterwarnings("ignore")
    
    genai.configure(api_key=api_key)
    
    # List available models
    print("\n📋 Available models:")
    available_models = []
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"   - {model.name}")
            available_models.append(model.name)
    
    # Try to use a model
    models_to_try = [
        'gemini-2.0-flash',
        'gemini-1.5-pro', 
        'gemini-1.5-flash',
        'gemini-pro',
        'gemini-1.0-pro'
    ]
    
    print("\n🧪 Testing content generation...")
    
    for model_name in models_to_try:
        try:
            # Check if model exists
            full_name = f"models/{model_name}"
            if not any(full_name in m for m in available_models):
                continue
                
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Say 'Hello!' in one word")
            print(f"\n✅ SUCCESS with {model_name}!")
            print(f"   Response: {response.text[:100]}")
            
            # Update the config recommendation
            print(f"\n💡 Use this model in your code:")
            print(f"   MODEL_NAME = '{model_name}'")
            break
        except Exception as e:
            print(f"   ❌ {model_name}: {str(e)[:50]}")
    else:
        print("\n❌ No working model found!")
        print("   Your API key might not have access to Gemini models.")
        print("   Please check: https://makersuite.google.com/app/apikey")
    
except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}: {str(e)}")

print("\n" + "=" * 50)
