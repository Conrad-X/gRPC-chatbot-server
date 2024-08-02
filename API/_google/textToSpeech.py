import os
import queue
import pygame
import threading
from io import BytesIO
from google.cloud import texttospeech
import pyaudio


audio_queue = queue.Queue()


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


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "api/_google/credentials.json"


# Instantiates a client
client = texttospeech.TextToSpeechClient()

# Set the text input to be synthesized

# Build the voice request, select the language code ("en-US") and the ssml
# voice gender ("neutral")
voice = texttospeech.VoiceSelectionParams(
    language_code="en-US", name="en-GB-Standard-A"
)

# Select the type of audio file you want returned
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.LINEAR16,
    speaking_rate=1.2,
)

# Create a queue for temperory audio files generated

# Perform the text-to-speech request on the text input with the selected
# voice parameters and audio file type


def textToSpeech(textToSpeak):
    synthesis_input = texttospeech.SynthesisInput(text=textToSpeak)
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    audio_queue.put(bytes(response.audio_content))


# def play_audio():
#     while True:
#         audio_file = audio_queue.get()
#         if audio_file is None:
#             continue

#         pygame.mixer.music.load(audio_file, "mp3")
#         # Play the audio
#         pygame.mixer.music.play()

#         # Wait for the audio to finish playing
#         while pygame.mixer.music.get_busy():
#             pygame.time.Clock().tick(5)


# Start the worker thread
worker_thread = threading.Thread(target=play_audio, daemon=True)
worker_thread.start()
# pygame.mixer.init()
