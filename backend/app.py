import sys
import os
import wave
from time import time
from typing import Optional
import pyaudio
import numpy as np
from io import BytesIO
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
from agent import Agent
from pydub import AudioSegment
from groq import Groq
from flask import Flask, request, jsonify
from flask_cors import CORS
import certifi
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import json
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

# Callback on connection
def on_connect(client, userdata, flags, rc):
    print(f'Connected (Result: {rc})')
    client.subscribe('response-topic')

# Callback when message is sent
def on_publish(client, userdata, mid):
    print(f'Sent message (Result: {mid})')

# Callback when message is received from
def on_message(client, userdata, message):
    print(f'Received message {message.payload}')

# Function to publish message
def send_message(client, location):
    topic = os.getenv('TOPIC')
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
    # client.on_message = on_message
    return "dummy route works"
