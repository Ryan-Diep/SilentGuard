from flask import Flask
import certifi
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import os
import json

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello World Flask"

@app.route("/dummy")
def dummy():
    send_message("Ottawa")
    return "dummy route works"

# Callback on connection
def on_connect(client, userdata, flags, rc):
    print(f'Connected (Result: {rc})')

# Callback when message is sent
def on_publish(client, userdata, mid):
    print(f'Sent message (Result: {mid})')

def send_message(location):
    # If using websockets (protocol is ws or wss), must set the transport for the client as below
    client = mqtt.Client()

    client.on_connect = on_connect
    client.on_publish = on_publish

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
    topic = os.getenv('TOPIC')
    client.publish(topic, location, qos=1)
    client.loop_stop()
    client.disconnect()
