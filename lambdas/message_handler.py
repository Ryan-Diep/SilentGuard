import os
from solace.messaging.messaging_service import MessagingService
from solace.messaging.receiver.message_receiver import MessageReceiver
from solace.messaging.resources.topic import Topic

def lambda_handler(event, context):
    solace_config = {
        "host": os.getenv("SOLACE_HOST"),
        "username": os.getenv("SOLACE_USERNAME"),
        "password": os.getenv("SOLACE_PASSWORD")
    }

    messaging_service = MessagingService.builder().from_properties(solace_config).build()
    messaging_service.connect()

    topic_subscription = Topic.of("message/processing??")
    receiver = messaging_service.create_direct_message_receiver_builder().with_subscription(topic_subscription).build()
    receiver.start()

    for message in receiver.receive_async():
        print(f"Received message: {message.get_payload_as_string()}")
        receiver.acknowledge(message)

    return {
        "statusCode": 200,
        "body": "Message handled successfully"
    }
