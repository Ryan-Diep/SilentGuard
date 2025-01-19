import json
import base64
import os
from groq import Groq
import paho.mqtt.client as mqtt

# Initialize MQTT Client
def setup_mqtt_client():
    client = mqtt.Client()

    client.username_pw_set(
        username=os.getenv("SOLACE_USERNAME"),
        password=os.getenv("SOLACE_PASSWORD")
    )

    client.connect(
        host=os.getenv("SOLACE_URL"),
        port=int(os.getenv("SOLACE_PORT"))
    )
    client.loop_start()
    return client

# Publish message to Solace
def publish_to_solace(client, message):
    topic = os.getenv("SOLACE_TOPIC")
    client.publish(topic, message, qos=1)
    print(f"Published message: {message} to topic: {topic}")


# Main handler
def lambda_handler(event, context):
    location = str(base64.b64decode(event['body']).decode('utf-8'))

    # Create Groq client
    client = Groq(
        api_key=os.getenv("API_KEY"),
    )

    # Get emergency number
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"What is the emergency number for the country with this address {location}? Respond with just the number.",
            }
        ],
        model="llama3-8b-8192",
    )
    response_content = chat_completion.choices[0].message.content
    # print(f"Groq response: {response_content}")

    # Publish to Solace
    mqtt_client = setup_mqtt_client()
    publish_to_solace(mqtt_client, f"The authorities have been notified.")

    return {
        'statusCode': 200,
        'body': json.dumps(response_content)
    }
