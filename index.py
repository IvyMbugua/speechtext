import requests
import time
import os


API_KEY = '8768a8e380ec448b9d1a8e28af0d2dbc'

upload_endpoint = 'https://api.assemblyai.com/v2/upload'
transcript_endpoint = 'https://api.assemblyai.com/v2/transcript'

headers_auth_only = {
    'authorization' : API_KEY
}

headers = {
    'authorization' : API_KEY,
    'content_type' : 'application/json'
}

CHUNK_SIZE = 5_242_800 #5MB

def upload(filename):
    print(f'Step 1: Uploading file {filename} ...', end='')

    def read_file(filename):

        with open(filename, 'rb') as file:
            while True:
                data = file.read(CHUNK_SIZE)
                if not data:
                    break
                yield data

    upload_response = requests.post(upload_endpoint,
                                    data = read_file(filename),
                                    headers = headers_auth_only)
    print('Uploading done.')
    return upload_response.json()['upload_url']


def transcribe(audio_url):
    print(f'Step 2: Start transciption... ')
    transcript_request = {
        'audio_url' : audio_url
    }

    transcript_response = requests.post(transcript_endpoint, json=transcript_request, headers=headers)

    print('Transcription done.')
    return transcript_response.json()['id']


def poll(transcript_id):
    polling_endpoint = f'{transcript_endpoint}/{transcript_id}'
    polling_response = requests.get(polling_endpoint, headers=headers)
    return polling_response.json()


def get_transcription_result(audio_url):
    transcribe_id = transcribe(audio_url)
    print(f'Step 3: Waiting for transcription results... ')
    while True:
        data = poll(transcribe_id)
        if data['status'] == 'completed':
            print('Transcription completed ')
            return data, None
        elif data['status'] == 'error':
            print('Transcription failed. ')
            return data, data['error']
        
        print('Waiting for 5 more seconds...')
        time.sleep(5)


def main(filename):
    audio_url = upload(filename)

    data, error = get_transcription_result(audio_url)
    if data:
        transcript = data['text']
        print(transcript)
    else:
        print('Error: ', error)

main('DanAudio.m4a')


