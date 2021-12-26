import json

import boto3
import telegram
import os

bot = telegram.Bot(token=os.getenv('bot_token'))

session = boto3.session.Session()
s3 = session.client(
    service_name='s3',
    aws_access_key_id=os.getenv('aws_id'),
    aws_secret_access_key=os.getenv('aws_secret'),
    endpoint_url='https://storage.yandexcloud.net'
)


def get_face_files(name):
    face_file = name.replace(' ', '_') + '.txt'
    try:
        return str(s3.get_object(Bucket=os.getenv('bucket'), Key=face_file)['Body'].read().decode('utf-8')).split('\n')
    except BaseException:
        return []


def save_face_files(files, name):
    face_file = name.replace(' ', '_') + '.txt'
    s3.put_object(Body="\n".join(files), Key=face_file, Bucket=os.getenv('bucket'))


def get_message_photo(message_id):
    return str(s3.get_object(Bucket=os.getenv('bucket'), Key=str(message_id))['Body'].read().decode('utf-8'))


def get_face_files_orig(name):
    files = get_face_files(name)
    orig_files = set()
    for file in files:
        ext = file.split('.')[-1]
        orig_name = file.split('_face_')[0]
        orig_files.add(orig_name + '.' + ext)
    return orig_files


def handler(event, context):
    body = json.loads(event['body'])
    message = body['message']
    chat_id = message['chat']['id']
    if 'reply_to_message' in message:
        reply_message_id = message['reply_to_message']['message_id']
        name = message['text']
        file_names = get_face_files(name)
        photo = get_message_photo(reply_message_id)
        save_face_files(file_names + [photo], name)
    if str(message['text']).strip().startswith('/find'):
        text = str(message['text'])
        name = text.replace('/find ', '')
        faces = get_face_files_orig(name)
        if not faces:
            bot.send_message(chat_id, 'Нет фото')
        else:
            for face in faces:
                bot.send_photo(chat_id, 'http://' + os.getenv('bucket') + '.website.yandexcloud.net/' + face)
    return {
        'statusCode': 200
    }
