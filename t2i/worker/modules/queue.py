import boto3
import os
import json
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv('AWS_REGION')
AWS_SQS_QUEUE_URL = os.getenv('AWS_SQS_QUEUE_URL')

sqs = boto3.client('sqs', region_name=AWS_REGION)

async def sqs_dequeue():
    try:
        response = sqs.receive_message(
            QueueUrl=AWS_SQS_QUEUE_URL,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=10  
        )
        messages = response.get('Messages', [])
        
        if not messages:
            print("No messages found.")
            return None

        for message in messages:
            body = json.loads(message['Body'])
            receipt_handle = message['ReceiptHandle']
            
            sqs.delete_message(
                QueueUrl=AWS_SQS_QUEUE_URL,
                ReceiptHandle=receipt_handle
            )
            
            print("Message deleted.")
            print(body['image_id'])
            return body['image_id']

    except Exception as e:
        print(f"Error occurred: {e}")
        return None

