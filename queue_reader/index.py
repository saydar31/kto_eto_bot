import boto3
import telegram
import os


def read_list(sting):
    b = sting[1:-1]
    return [s.strip()[1:-1] for s in b.split(',')]


class FaceSender:

    def __init__(self, token, secret, bot_token):
        self.bot = telegram.Bot(token=bot_token)
        session = boto3.session.Session()
        self.s3 = session.client(
            service_name='s3',
            aws_access_key_id=token,
            aws_secret_access_key=secret,
            endpoint_url='https://storage.yandexcloud.net'
        )
        self.sqs = boto3.client(
            service_name='sqs',
            aws_access_key_id=token,
            aws_secret_access_key=secret,
            endpoint_url='https://message-queue.api.cloud.yandex.net',
            region_name='ru-central1'
        )
        self.storage_name = os.getenv('bucket')
        self.chat_id = os.getenv('chat_id')

    def read_faces(self):
        messages = self.sqs.receive_message(
            QueueUrl=os.getenv('queue_url'),
            MaxNumberOfMessages=10,
            VisibilityTimeout=60,
            WaitTimeSeconds=20
        ).get('Messages')
        result = []
        for msg in messages:
            result += read_list(msg.get('Body'))
            self.sqs.delete_message(
                QueueUrl=os.getenv('queue_url'),
                ReceiptHandle=msg.get('ReceiptHandle')
            )
        return result

    def send_faces(self):
        faces = self.read_faces()
        for face in faces:
            message = self.bot.send_photo(self.chat_id,
                                          'http://' + self.storage_name + '.website.yandexcloud.net/' + face,
                                          caption='Кто это?')
            self.s3.put_object(Body=face, Bucket=self.storage_name, Key=str(message.message_id))


def handler(request, context):
    face_sender = FaceSender(os.getenv('aws_id'), os.getenv('aws_secret'),
                             os.getenv('bot_token'))
    face_sender.send_faces()
