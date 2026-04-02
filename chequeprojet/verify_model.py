import google.generativeai as genai

genai.configure(api_key="AIzaSyALNXMUxpVnDQ9-jVlVo02rXjLC0hwCSy0")

try:
    print("Trying to get model 'models/gemini-1.5-flash'...")
    m = genai.get_model("models/gemini-1.5-flash")
    print(f"Model found: {m.name}")
    print(f"Supported methods: {m.supported_generation_methods}")
except Exception as e:
    print(f"Error getting model: {e}")
