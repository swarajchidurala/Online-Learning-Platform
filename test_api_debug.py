from google import genai
import os

API_KEY="AIzaSyAzF8eLXknsJW55atnR9qVgzaA9Ync-PC0"

try:
    print(f"Testing Gemini API with key: {API_KEY[:5]}... and model: gemini-1.5-flash")
    client = genai.Client(api_key=API_KEY)
    response = client.models.generate_content(
        model="gemini-3-flash-preview", 
        contents="Say hello"
    )
    print("Success! Response:")
    print(response.text)
except Exception as e:
    print("API Call Failed!")
    print(f"Error Type: {type(e).__name__}")
    print(f"Error Message: {e}")
