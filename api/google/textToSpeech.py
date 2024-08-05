import os
import queue
import threading
import pyaudio
from google.cloud import texttospeech

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "api/google/credentials.json"

# Audio queue to store syntesized speech as a stream
audio_queue = queue.Queue()


# Open a stream with pyaudio to be played on a worker thread
def play_audio():
    player = pyaudio.PyAudio()
    stream = player.open(
        rate=22050,
        channels=1,
        format=pyaudio.paInt16,
        output=True,
        frames_per_buffer=4096,
    )
    while True:
        if not audio_queue.empty():
            stream.write(audio_queue.get())


# Start the worker thread
worker_thread = threading.Thread(target=play_audio, daemon=True)
worker_thread.start()


# Instantiates a client
client = texttospeech.TextToSpeechClient()

# Build the voice request, select the language code ("en-US")
voice = texttospeech.VoiceSelectionParams(
    language_code="en-US", name="en-GB-Standard-A"
)

# Select the type of audio file you want returned
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.LINEAR16,
    speaking_rate=1.2,
)


# Perform the text-to-speech request on the text input with the selected
# voice parameters and audio file type
def textToSpeech(textToSpeak):
    if not textToSpeak[0].isalnum() and textToSpeak[0] != " ":
        textToSpeak = textToSpeak[1:]
    synthesis_input = texttospeech.SynthesisInput(text=textToSpeak)
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    audio_queue.put(bytes(response.audio_content))
