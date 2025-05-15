import os
from dotenv import load_dotenv
import requests
from logger_config import logger
from gemini_client import GeminiAPIClient
import json
from datetime import datetime

load_dotenv()

GLADIA_API_KEY = os.getenv("GLADIA_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GLADIA_API_KEY is None:
    logger.warning("GLADIA_API_KEY is not set in the environment variables.")
    raise ValueError("GLADIA_API_KEY is not set in the environment variables.")

if GEMINI_API_KEY is None:
    logger.warning("GEMINI_API_KEY is not set in the environment variables.")
    raise ValueError("GEMINI_API_KEY is not set in the environment variables.")

GMC = GeminiAPIClient(api_key=GEMINI_API_KEY)

def generate_content(user_input: str):
    logger.debug("starting generating content with Gemini API...")
    response = GMC.generate(user_input)
    logger.debug("Content generated successfully.")
    return response 

def save_as_json(response_text, transcription ,filename):
    clean_text = response_text.strip().strip("```json").strip("```").strip()
    response_data = json.loads(clean_text)
    filename = filename.split('/')[-1].split('.')[0]
    timestamp = datetime.now().strftime("%b %d , %Y , %I:%M %p")
    # Save to a file
    with open(f"responses/{filename}.json", "w", encoding="utf-8") as f:
        response_data['transcription'] = transcription
        response_data['timestamp'] = timestamp
        json.dump(response_data, f, indent=4, ensure_ascii=False)
    logger.info(f"Saved as responses/{filename}.json")

def audio_transcription(filepath: str):
    headers = {'x-gladia-key': GLADIA_API_KEY}
    filename = filepath.split('/')[-1].split('.')[0]
    filename, file_ext = os.path.splitext(filepath)
    with open(filepath, 'rb') as audio:
        files = {
            'audio': (filename, audio, f'audio/{file_ext[1:]}'), 
            'toggle_diarization': (None, 'true'),  
            'diarization_max_speakers': (None, '2'), 
            'output_format': (None, 'txt')
        }
        logger.debug('Sending request to Gladia API...')
        # Make the POST request
        response = requests.post(
            'https://api.gladia.io/audio/text/audio-transcription/',
            headers=headers,
            files=files
        )
        if response.status_code == 200:
            response_data = response.json()
            prediction = response_data.get('prediction', '')
            return prediction
        else:
            logger.error('Request failed with status:', response.status_code)
            logger.error('Error response:', response.text)
            return None

# Example usage
if __name__ == '__main__':
    source_file = "audio/audio.mp3"
    if not os.path.exists(source_file):
        logger.error(f"File {source_file} does not exist.")
        raise FileNotFoundError(f"File {source_file} does not exist.")
    logger.info("Transcribing audio...")
    transcription = audio_transcription(source_file)
    if transcription:
        logger.debug("Transcription successful.")
        logger.info("Rewriting as markdown...")
        gen_ai_content = generate_content(transcription)
        logger.info(f"gen_ai_content generated for {source_file} ")
        save_as_json(
            transcription=transcription, response_text=gen_ai_content, filename=source_file
        )
    else:
        logger.error("Transcription failed.")
