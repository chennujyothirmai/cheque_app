import google.generativeai as genai

genai.configure(api_key="AIzaSyALNXMUxpVnDQ9-jVlVo02rXjLC0hwCSy0")

print("Checking available models and versions...")
try:
    with open('available_models.txt', 'w') as f:
        for m in genai.list_models():
            f.write(f"{m.name} : {m.supported_generation_methods}\n")
    print("Models list saved to available_models.txt")
except Exception as e:
    print(f"Error: {e}")
