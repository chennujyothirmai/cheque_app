import google.generativeai as genai

genai.configure(api_key="AIzaSyALNXMUxpVnDQ9-jVlVo02rXjLC0hwCSy0")

print("Listing models with GenerateContent support:")
try:
    models = list(genai.list_models())
    for m in models:
        if 'generateContent' in m.supported_generation_methods:
            print(f" - {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")

try:
    print(f"Default Gemini Flash name: {genai.GenerativeModel('gemini-1.5-flash').model_name}")
except Exception as e:
    print(f"Error initializing gemini-1.5-flash: {e}")
