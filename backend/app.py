import os
from threading import Thread
import wave
from time import time
from typing import Optional
import pyaudio
import numpy as np
from io import BytesIO
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
from agent import Agent
from parser import find_location, find_voice
from pydub import AudioSegment
from groq import Groq
from flask import Flask, request, jsonify
from flask_cors import CORS
import certifi
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from config import (
    ELEVENLABS_API_KEY,
    GROQ_API_KEY,
    FORMAT,
    CHANNELS,
    RATE,
    CHUNK,
    SILENCE_THRESHOLD,
    SILENCE_DURATION,
    PRE_SPEECH_BUFFER_DURATION,
    Voices
)

app = Flask(__name__)
CORS(app)

call_made = False
voice_undetermined = True
current_assistant_thread = None
assistant = None

# Callback on connection
def on_connect(client, userdata, flags, rc):
    print(f'Connected (Result: {rc})')
    client.subscribe(os.getenv('RESPONSE_TOPIC'))

# Callback when message is sent
def on_publish(client, userdata, mid):
    print(f'Sent message (Result: {mid})')

# Callback when message is received from
def on_message(client, userdata, message):
    print(f'Received message {message.payload}')
    global call_made
    call_made = True

# Function to publish message
def send_message(client, location):
    topic = os.getenv('PUBLISH_TOPIC')
    client.publish(topic, location, qos=1)

client = mqtt.Client()

client.on_connect = on_connect
client.on_publish = on_publish
client.on_message = on_message

# Required if using TLS endpoint (mqtts, wss, ssl), remove if using plaintext
# Use Mozilla's CA bundle
client.tls_set(ca_certs=certifi.where())

# Enter your password here
# Get the parent directory of the current file
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Build the path to the .env file
dotenv_path = os.path.join(parent_dir, ".env")
load_dotenv(dotenv_path)
client.username_pw_set('solace-cloud-client', os.getenv('PASSWORD'))

# Use the host and port from Solace Cloud without the protocol
client.connect(os.getenv('SOLACE_URL'), int(os.getenv('PORT')))
client.loop_start()

@app.route("/")
def home():
    return "Hello World Flask"

@app.route("/dummy")
def dummy():
    send_message(client, "Ottawa")
    return "dummy route works"

@app.route("/start_call", methods=["POST"])
def start_call():
    global current_assistant_thread, assistant

    data = request.get_json()
    activation_phrase = data.get("activationPhrase")
    confirmation_phrase = data.get("confirmationPhrase")

    # Log or process the received data
    print(f"Activation Phrase: {activation_phrase}")
    print(f"Confirmation Phrase: {confirmation_phrase}")

    assistant = VoiceAssistant(activation_phrase, confirmation_phrase)
    # assistant.run()
    current_assistant_thread = Thread(target=assistant.run, daemon=True)
    current_assistant_thread.start()

    # Respond back to the client
    return jsonify({"message": "Call started successfully!"}), 200

@app.route("/end_call", methods=["POST"])
def end_call():
    global current_assistant_thread, assistant
    if current_assistant_thread and current_assistant_thread.is_alive():
        assistant.stop()
        current_assistant_thread.join(timeout=5)
        current_assistant_thread = None
        assistant = None
        return jsonify({"message": "Call stopped successfully!"}), 200
    
    return jsonify({"message": "No active call to stop"}), 400

class VoiceAssistant:
    def __init__(
        self,
        activation_phrase,
        confirmation_phrase,
        voice_id: Optional[str] = Voices.CHARLIE,
    ):
        self.audio = pyaudio.PyAudio()
        self.agent = Agent(confirmation_phrase)
        self.voice_id = voice_id
        self.xi_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        self.g_client = Groq(api_key=GROQ_API_KEY)
        self.activation_phrase = activation_phrase
        self.location = "Canada"
        self.running = True

    def stop(self):
        self.running = False

    def is_silence(self, data):
        """
        Detect if the provided audio data is silence.

        Args:
            data (bytes): Audio data.

        Returns:
            bool: True if the data is considered silence, False otherwise.
        """
        audio_data = np.frombuffer(data, dtype=np.int16)
        rms = np.sqrt(np.mean(audio_data**2))
        return rms < SILENCE_THRESHOLD

    def listen_for_speech(self):
        """
        Continuously detect silence and start recording when speech is detected.
        
        Returns:
            BytesIO: The recorded audio bytes.
        """
        stream = self.audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
        print("Listening for speech...")
        pre_speech_buffer = []
        pre_speech_chunks = int(PRE_SPEECH_BUFFER_DURATION * RATE / CHUNK)

        while True:
            data = stream.read(CHUNK)
            pre_speech_buffer.append(data)
            if len(pre_speech_buffer) > pre_speech_chunks:
                pre_speech_buffer.pop(0)

            if not self.is_silence(data):
                print("Speech detected, start recording...")
                stream.stop_stream()
                stream.close()
                return self.record_audio(pre_speech_buffer)

    def record_audio(self, pre_speech_buffer):
        """
        Record audio until silence is detected.

        Args:
            pre_speech_buffer (list): Buffer containing pre-speech audio data.

        Returns:
            BytesIO: The recorded audio bytes.
        """
        stream = self.audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
        frames = pre_speech_buffer.copy()

        silent_chunks = 0
        while True:
            data = stream.read(CHUNK)
            frames.append(data)
            if self.is_silence(data):
                silent_chunks += 1
            else:
                silent_chunks = 0
            if silent_chunks > int(RATE / CHUNK * SILENCE_DURATION):
                break

        stream.stop_stream()
        stream.close()

        audio_bytes = BytesIO()
        with wave.open(audio_bytes, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(self.audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
        audio_bytes.seek(0)

        return audio_bytes

    def speech_to_text(self, audio_bytes):
        """
        Transcribe speech to text using Groq.

        Args:
            audio_bytes (BytesIO): The audio bytes to transcribe.

        Returns:
            str: The transcribed text.
        """
        start = time()
        audio_bytes.seek(0)
        transcription = self.g_client.audio.transcriptions.create(
            file=("temp.wav", audio_bytes.read()),
            model="distil-whisper-large-v3-en",
        )
        end = time()
        print(transcription)
        return transcription.text

    def text_to_speech(self, text, voice_id: Optional[str] = None):
        """
        Convert text to speech and return an audio stream.

        Args:
            text (str): The text to convert to speech.

        Returns:
            BytesIO: The audio stream.
        """
        voice_id = voice_id or self.voice_id
        response = self.xi_client.text_to_speech.convert(
            voice_id=voice_id,
            optimize_streaming_latency="0",
            output_format="mp3_22050_32",
            text=text,
            model_id="eleven_turbo_v2_5",
        )

        audio_stream = BytesIO()

        for chunk in response:
            if chunk:
                audio_stream.write(chunk)

        audio_stream.seek(0)
        return audio_stream

    def audio_stream_to_iterator(self, audio_stream, format='mp3'):
        """
        Convert audio stream to an iterator of raw PCM audio bytes.

        Args:
            audio_stream (BytesIO): The audio stream.
            format (str): The format of the audio stream.

        Returns:
            bytes: The raw PCM audio bytes.
        """
        audio = AudioSegment.from_file(audio_stream, format=format)
        audio = audio.set_frame_rate(22050).set_channels(2).set_sample_width(2)  # Ensure the format matches pyaudio parameters
        raw_data = audio.raw_data

        chunk_size = 1024  # Adjust as necessary
        for i in range(0, len(raw_data), chunk_size):
            yield raw_data[i:i + chunk_size]

    def stream_audio(self, audio_bytes_iterator, rate=22050, channels=2, format=pyaudio.paInt16):
        """
        Stream audio in real-time.

        Args:
            audio_bytes_iterator (bytes): The raw PCM audio bytes.
            rate (int): The sample rate of the audio.
            channels (int): The number of audio channels.
            format (pyaudio format): The format of the audio.
        """
        stream = self.audio.open(format=format,
                                 channels=channels,
                                 rate=rate,
                                 output=True)

        try:
            for audio_chunk in audio_bytes_iterator:
                stream.write(audio_chunk)
        finally:
            stream.stop_stream()
            stream.close()
    
    def chat(self, query: str, call_made: bool=False) -> str:
        start = time()
        if call_made:
            response = self.agent.chat(query, False, True)
            end = time()
            print(f"Response: {response}\nResponse Time: {end - start}")
            return response
        response = self.agent.chat(query)
        end = time()
        print(f"Response: {response}\nResponse Time: {end - start}")
        return response

    def run(self):
        """
        Main function to run the voice assistant.
        """
        global call_made, voice_undetermined

        while self.running:
            # STT
            audio_bytes = self.listen_for_speech()
            text = self.speech_to_text(audio_bytes)

            if not self.running:
                break

            if call_made:
            # Agent
                response_text = self.chat(text, True)
                
                # TTS
                audio_stream = self.text_to_speech(response_text)
                audio_iterator = self.audio_stream_to_iterator(audio_stream)
                self.stream_audio(audio_iterator)
                call_made = False
                self.agent.system_prompt = """\
                                            You are part of a realtime voice to voice interaction with the human. \
                                            You are playing the role of a trusted person the user chooses to talk to, like a parent, sibling, or friend. \
                                            Respond naturally, showing understanding and engagement with what the user says. Avoid asking specific personal questions or mentioning details like family members, pets, or locations unless the user brings them up first. \
                                            Maintain a calm and supportive tone, and ensure your responses feel conversational and realistic. \
                                            Respond with fill words like `hmm`, `ohh`, and similar wherever relevant to make your responses sound natural. \
                                            """
            
            else:
                response_text = self.chat(text, False)
                
                if voice_undetermined:
                    if find_voice(text) == "woman":
                        self.voice_id = Voices.JESSICA
                    else:
                        self.voice_id = Voices.CHARLIE
                    voice_undetermined = False

                location = find_location(text)
                if location != "None":
                    self.location = location

                if self.activation_phrase in text.lower():
                    print("Activation Phrase Detected")
                    print(self.location)
                    send_message(client, self.location)

                # TTS
                audio_stream = self.text_to_speech(response_text)
                audio_iterator = self.audio_stream_to_iterator(audio_stream)
                self.stream_audio(audio_iterator)


        