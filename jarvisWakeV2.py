import os
from dotenv import load_dotenv
import pvporcupine
import struct
import pyaudio
import pyttsx3
import time
from langchain_community.llms import Ollama
import speech_recognition as sr
from os import system
import sys




load_dotenv()

print(os.getenv('picovoice'))

print(os.getenv('keyWordPath'))

ACCESS_KEY = os.getenv('picovoice')

KEYWORD_PATH = os.getenv('keyWordPath')

# Initialize the Speech to Text engine
engine = pyttsx3.init()


# Create a recognizer object for Automatic Speech Recognition
r = sr.Recognizer()
source = sr.Microphone()




def respond(text):
    if sys.platform == 'darwin':
        ALLOWED_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,?!-_$:+-/ ")
        clean_text = ''.join(c for c in text if c in ALLOWED_CHARS)
        system(f"say '{clean_text}'")
    else:
        engine.say(text)
        engine.runAndWait()

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
            # Use the microphone as the audio source
            with source as s:
                print("Listening...")
                r.adjust_for_ambient_noise(s)
                audio = r.listen(s)
                
                print("Listening............")
                respond("Let me think about it.")
            try:

                # engine.say("Thinking")
                # engine.runAndWait()
                respond("Thinking")

                # Use Google's speech recognition to convert the audio to text
                text = r.recognize_google(audio)
                print("You said: " + text)

                # Add a short response
                short_response = "think step by step and Answer in 1 sentence or less keep the response short" + text
                print(short_response)

                # Ask the llm the message
                response = llm.invoke(short_response)
                
                # Speak the text
                print(f"Response is {response}")
                # engine.say(response)
                # engine.runAndWait()
                respond(response)


            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))


def main():

    think()
    # time.sleep(1)
    # respond("Goodbye.")



if __name__ == '__main__':
    main()
