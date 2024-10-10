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



# async def sqs_dequeue():
#     try:
#         response = sqs.receive_message(
#             QueueUrl=AWS_SQS_QUEUE_URL,
#             MessageAttributeNames = ['ip'],
#             MaxNumberOfMessages=1,
#             WaitTimeSeconds=10  
#         )
#         messages = response.get('Messages', [])
        
#         if not messages:
#             print("No messages found.")
#             return None

#         for message in messages:
#             body = json.loads(message['Body'])
#             receipt_handle = message['ReceiptHandle']
            
#             sqs.delete_message(
#                 QueueUrl=AWS_SQS_QUEUE_URL,
#                 ReceiptHandle=receipt_handle
#             )
            
#             print("Message deleted.")
#             return body['image_id']

#     except Exception as e:
#         print(f"Error occurred: {e}")
#         return None

# async def sqs_dequeue():
#     try:
#         if message['Attributes'].get('MessageGroupId') == 'ip':
#             response = sqs.receive_message(
#                 QueueUrl=AWS_SQS_QUEUE_URL,
#                 MessageAttributeNames = ['All'],
#                 MaxNumberOfMessages=1,
#                 WaitTimeSeconds=10  
#             )
#             messages = response.get('Messages', [])
            
#             if not messages:
#                 print("No messages found.")
#                 return None
            
#             for message in messages:
#                 body = json.loads(message['Body'])
#                 receipt_handle = message['ReceiptHandle']
                
#                 sqs.delete_message(
#                     QueueUrl=AWS_SQS_QUEUE_URL,
#                     ReceiptHandle=receipt_handle
#                 )
            
#             print("Message deleted.")
#             return body['image_id']

#     except Exception as e:
#         print(f"Error occurred: {e}")
#         return None


# async def sqs_dequeue():
#     messages = []
    
#     response = sqs.receive_message(
#         QueueUrl=AWS_SQS_QUEUE_URL,
#         AttributeNames=['All'],
#         MaxNumberOfMessages=1, 
#         WaitTimeSeconds=10  # 대기 시간 (long polling)
#     )
    
#     # 메시지가 있는 경우 처리
#     if 'Messages' in response:
#         for message in response['Messages']:
#             # 메시지의 메시지 그룹 ID가 요청한 그룹 ID와 일치하는지 확인
#             if message['Attributes'].get('MessageGroupId') == 'ip':
#                 messages.append(message)
#                 print(f"Received message: {message['Body']}")
#                 body = json.loads(message['Body'])
#                 receipt_handle = message['ReceiptHandle']
                
#                 # 메시지 삭제 (선택적)
#                 sqs.delete_message(
#                     QueueUrl=AWS_SQS_QUEUE_URL,
#                     ReceiptHandle=receipt_handle
#                 )
#     else:
#         print("No messages received")

#     return body['image_id']