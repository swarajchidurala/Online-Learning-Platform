from google import genai



client = genai.Client(api_key="AIzaSyAzF8eLXknsJW55atnR9qVgzaA9Ync-PC0")


def get_gemini_response(user_input):
    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview", contents=user_input
        )
        return response.text
    except Exception as e:
        return str(e)

def generate_test_questions(course_title, course_description):
    prompt = f"""
    Create a test for the course '{course_title}' with the following description: '{course_description}'.
    
    Generate exactly:
    - 10 Multiple Choice Questions (MCQ)
    - 2 Multiple Select Questions (MSQ)
    - 3 Coding conceptual/scenario-based questions (if applicable, else add more MCQs)
    
    The total number of questions must be 15.
    
    Return the response in strictly valid JSON format with this structure:
    {{
        "questions": [
            {{
                "id": 1,
                "type": "mcq",  // or "msq" for multiple select
                "question": "Question text here",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": "Option B" // or ["Option A", "Option C"] for msq
            }}
        ]
    }}
    Do not include any markdown formatting (like ```json), just the raw JSON string.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview", contents=prompt,
             config={
                'response_mime_type': 'application/json'
            }
        )
        return response.text
    except Exception as e:
        return str(e)
