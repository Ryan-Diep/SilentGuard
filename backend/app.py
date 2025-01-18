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
    # client = mqtt.Client(transport='websockets')
    client = mqtt.Client()

    client.on_connect = on_connect
    client.on_publish = on_publish

    # Required if using TLS endpoint (mqtts, wss, ssl), remove if using plaintext
    # Use Mozilla's CA bundle
    client.tls_set(ca_certs=certifi.where())

    # Enter your password here
    load_dotenv()
    client.username_pw_set('solace-cloud-client', os.getenv('PASSWORD'))

    # Use the host and port from Solace Cloud without the protocol
    client.connect(os.getenv('SOLACE_URL'), int(os.getenv('PORT')))

    client.loop_start()
    topic = "keyword-detected"
    client.publish(topic, json.dumps({"location": location}))
    client.loop_stop()
    client.disconnect()
