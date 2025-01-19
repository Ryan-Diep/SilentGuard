import json
import base64
import os
from groq import Groq
import paho.mqtt.client as mqtt
import certifi

# Global MQTT client
mqtt_client = None

def setup_mqtt_client():
    global mqtt_client
    if mqtt_client is None:
        mqtt_client = mqtt.Client()
        mqtt_client.tls_set(ca_certs=certifi.where())
        mqtt_client.username_pw_set(username=os.getenv("SOLACE_USERNAME"), password=os.getenv("SOLACE_PASSWORD"))
        mqtt_client.connect(host=os.getenv("SOLACE_URL"), port=int(os.getenv("SOLACE_PORT")))
        mqtt_client.loop_start()
    return mqtt_client

def publish_to_solace_async(client, message):
    topic = os.getenv("SOLACE_TOPIC")
    client.publish(topic, message, qos=1)
    client.loop_stop()
    print(f"Published message: {message} to topic: {topic}")

def get_groq_responses(client, location):
    emergency_number_response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"What is the emergency number for the country with this address {location}? Respond with just the number.",
            }
        ],
        model="llama3-8b-8192",
        temperature=0.1,
    )
    emergency_number = emergency_number_response.choices[0].message.content

    simulated_call_response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"""You are someone calling the Police on behalf of someone reporting an emergency. 
                Provide the police with only factual details that were given.
                You are reporting someone's location and that they are in danger. Keep it short and to the point.""",
            }
        ],
        model="llama3-8b-8192",
        temperature=0.1,
    )
    simulated_police_call = simulated_call_response.choices[0].message.content
    return emergency_number, simulated_police_call

# Main handler
def lambda_handler(event, context):
    # Decode the location from the event
    location = str(base64.b64decode(event['body']).decode('utf-8'))

    # Create Groq client
    groq_client = Groq(
        api_key=os.getenv("API_KEY"),
    )

    # Get responses from Groq
    emergency_number, simulated_police_call = get_groq_responses(groq_client, location)
    print("Emergency number: " + emergency_number)

    # Publish to Solace
    mqtt_client = setup_mqtt_client()
    publish_to_solace_async(mqtt_client, "The authorities have been notified.")

    print("Groq simulated 'script' emergency call: " + simulated_police_call)

    return {
        'statusCode': 200,
        'body': json.dumps("")
    }
