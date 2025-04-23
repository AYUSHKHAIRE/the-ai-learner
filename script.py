import os
from dotenv import load_dotenv
import requests

# Load environment variables from a .env file
load_dotenv()

# Get the Gladia API key from the environment
GLADIA_API_KEY = os.getenv("GLADIA_API_KEY")

# Raise an error if the key is not found
if GLADIA_API_KEY is None:
    raise ValueError("GLADIA_API_KEY is not set in the environment variables.")

def audio_transcription(filepath: str):
    # Define API key as a header
    headers = {'x-gladia-key': GLADIA_API_KEY}
    filename, file_ext = os.path.splitext(filepath)

    with open(filepath, 'rb') as audio:
        files = {
            'audio': (filename, audio, f'audio/{file_ext[1:]}'),  # audio/mp3 or similar
            'toggle_diarization': (None, 'true'),  # Use string for boolean values in multipart/form-data
            'diarization_max_speakers': (None, '2'),  # Also string
            'output_format': (None, 'txt')
        }

        print('Sending request to Gladia API...')
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
            print('Request failed with status:', response.status_code)
            print('Error response:', response.text)
            return None

# Example usage
if __name__ == '__main__':
    transcription = audio_transcription("audio.mp3")
    if transcription:
        print("Transcript:", transcription)
