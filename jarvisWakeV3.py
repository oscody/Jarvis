import os
from dotenv import load_dotenv
import pvporcupine
import struct
import pyaudio
import time
from langchain_community.llms import Ollama
import speech_recognition as sr
from os import system
import sys
from gtts import gTTS  # Import gTTS

load_dotenv()

print(os.getenv('picovoice'))
print(os.getenv('keyWordPath'))

ACCESS_KEY = os.getenv('picovoice')
KEYWORD_PATH = os.getenv('keyWordPath')

# Create a recognizer object for Automatic Speech Recognition
r = sr.Recognizer()
source = sr.Microphone()

def respond(text):
    if sys.platform == 'darwin':
        ALLOWED_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,?!-_$:+-/ ")
        clean_text = ''.join(c for c in text if c in ALLOWED_CHARS)
        system(f"say '{clean_text}'")
    else:
        tts = gTTS(text=text, lang='en')  # Use gTTS here
        tts.save("temp.mp3")  # Save the speech to a temporary file
        os.system("mpg321 temp.mp3")  # Use a player like mpg321, afplay (on macOS) or a similar command to play the saved audio file
        os.remove("temp.mp3")  # Optionally remove the temporary file after playing

def wake_word_detection():
    porcupine = None
    pa = None
    audio_stream = None

    try:
        porcupine = pvporcupine.create(
            access_key=ACCESS_KEY,
            keyword_paths=[KEYWORD_PATH]
        )

        pa = pyaudio.PyAudio()

        audio_stream = pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length)

        while True:
            pcm = audio_stream.read(porcupine.frame_length)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

            result = porcupine.process(pcm)

            if result >= 0:
                print("Wake word detected!")
                return True

    finally:
        if audio_stream is not None:
            audio_stream.close()

        if pa is not None:
            pa.terminate()

        if porcupine is not None:
            porcupine.delete()

def think():
    # Initialize the Ollama model
    model = "tinyllama"
    llm = Ollama(model=model)

    while True:
        if wake_word_detection():
            with source as s:
                print("Listening...")
                r.adjust_for_ambient_noise(s)
                audio = r.listen(s)
                
                print("Listening............")
                respond("Let me think about it.")
            try:
                respond("Thinking")
                
                # Use Google's speech recognition to convert the audio to text
                text = r.recognize_google(audio)
                print("You said: " + text)

                # Add a short response
                short_response = "think step by step and Answer in 1 sentence or less keep the response short " + text
                print(short_response)

                # Ask the llm the message
                response = llm.invoke(short_response)
                
                # Speak the text
                print(f"Response is {response}")
                respond(response)

            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))

def main():
    think()

if __name__ == '__main__':
    main()
