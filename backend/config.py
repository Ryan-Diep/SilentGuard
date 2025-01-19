import os
from dotenv import load_dotenv
import pyaudio
from enum import Enum

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

dotenv_path = os.path.join(parent_dir, ".env")
load_dotenv(dotenv_path)
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not ELEVENLABS_API_KEY:
    raise ValueError("ELEVENLABS_API_KEY environment variable not set")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable not set")


class Voices(Enum):
    CHARLIE = "IKne3meq5aSn9XLyUdCD"
    ADAM = "pNInz6obpgDQGcFmaJgB" 

VOICE_ID = Voices.ADAM
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
SILENCE_THRESHOLD = 200  # Adjust this threshold as needed
SILENCE_DURATION = 2  # Duration of silence to stop recording in seconds
PRE_SPEECH_BUFFER_DURATION = 0.5  # 500ms of audio to keep before speech detection