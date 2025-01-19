import json
import base64
from groq import Groq
import os

def lambda_handler(event, context):
    print(event['body'])
    location = str(base64.b64decode(event['body']))
    print(f"Decoded location: {location}")

    client = Groq(
        api_key=os.getenv("API_KEY"),
    )

    # Generate a chat completion using the Groq client
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"What is the weather in {location} today?",
            }
        ],
        model="llama3-8b-8192",
    )

    response_content = chat_completion.choices[0].message.content
    print(f"Groq response: {response_content}")

    return {
        'statusCode': 200,
        'body': json.dumps(response_content)
    }
