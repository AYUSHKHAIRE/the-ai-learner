from logger_config import logger
import google.generativeai as genai

class GeminiAPIClient:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config=genai.types.GenerationConfig(
                temperature=2,
                top_p=0.95,
                top_k=40,
                max_output_tokens=8192
            )
        )
        logger.info("Gemini API client initialized.")

    def generate(self, user_input):
        logger.debug("Generating content with Gemini API...")

        prompt = f"""
Please rewrite the following text as a markdown file.
Give a summary as well.
The output should be JSON like this:

{{
    "markdown": "markdown text", 
    "summary": "summary text",
    "tags": [
        "tag1",
        "tag2",
        "tag2",
        "tag3"
    ],
    "title": "title text"
}}

THE GIVEN TEXT IS: {user_input}
"""

        response = self.model.generate_content(prompt)
        return response.text
