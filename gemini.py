from google import genai



client = genai.Client(api_key="AIzaSyD9IqO5BoFVMYsVKZI7_EIFyj6k2RxoCUc")


def get_gemini_response(user_input):
    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview", contents=user_input
        )
        return response.text
    except Exception as e:
        return str(e)
