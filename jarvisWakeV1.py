import os
from dotenv import load_dotenv
import pvporcupine
import struct
import pyaudio
import pyttsx3
from langchain_community.llms import Ollama
import speech_recognition as sr

load_dotenv()

print(os.getenv('picovoice'))

print(os.getenv('keyWordPath'))

ACCESS_KEY = os.getenv('picovoice')

KEYWORD_PATH = os.getenv('keyWordPath')

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

def main():
    # Initialize the Ollama model
    model = "tinyllama"
    llm = Ollama(model=model)

    # Initialize the Speech to Text engine
    engine = pyttsx3.init()

    # Create a recognizer object for Automatic Speech Recognition
    r = sr.Recognizer()

    while True:
        if wake_word_detection():
            # Use the microphone as the audio source
            with sr.Microphone() as source:
                print("Listening...")
                audio = r.listen(source)

            try:
                # Use Google's speech recognition to convert the audio to text
                text = r.recognize_google(audio)
                print("You said: " + text)

                # Add a short response
                short_response = "think step by step and Answer in 1 sentence or less keep the response short" + text
                print(short_response)


                # Start the thinking thread
                #thinking_thread = threading.Thread(target=thinking)
                #thinking_thread.start()

                # Ask the llm the message
                response = llm.invoke(short_response)
                


                # Stop the thinking thread
                #thinking_thread.do_run = False
                #thinking_thread.join()


                # Speak the text
                print(f"Response is {response}")
                engine.say(response)
                engine.runAndWait()

            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))

if __name__ == '__main__':
    main()