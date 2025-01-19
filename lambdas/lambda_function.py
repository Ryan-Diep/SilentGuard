import json
import base64
from groq import Groq
import os

def lambda_handler(event, context):
    location = str(base64.b64decode(event['body']).decode('utf-8'))

    client = Groq(
        api_key=os.getenv("API_KEY"),
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"What is the countries mergency number for the country with this address {location}? Respond with just the number.",
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
