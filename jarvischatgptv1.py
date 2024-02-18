# code not working 

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
import datetime
import pytz
from openai import OpenAI


load_dotenv()


OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=OPENAI_API_KEY)  # Initialize the client with the API key




# print(os.getenv('picovoice'))
# print(os.getenv('keyWordPath'))

ACCESS_KEY = os.getenv('picovoice')
KEYWORD_PATH = os.getenv('keyWordPath')
GazaBoglePath = os.getenv('gazaBogle')

# Create a recognizer object for Automatic Speech Recognition
r = sr.Recognizer()
source = sr.Microphone()

# Define a log file location
log_file = os.getenv("CHAT_HISTORY_LOG_PATH", "ChatSummary.log")


def log_to_file(text):
    # Get current time in Eastern Time Zone
    eastern = pytz.timezone('US/Eastern')
    now = datetime.datetime.now(eastern)
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S %Z")

    with open(log_file, "a") as file:
        file.write(f"{timestamp}: {text}\n")

def respond(text):

    # Log the text with date and time to a file
    log_to_file(text)


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
            keyword_paths=[KEYWORD_PATH,GazaBoglePath]
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


    while True:
        if wake_word_detection():
            respond("Ask me a question. I am listening.")

            with source as s:
                print("Listening...")
                r.adjust_for_ambient_noise(s)
                
                try:
                    # Wait for a question with a timeout (e.g., 5 seconds)
                    audio = r.listen(s, timeout=10)
                    print("Listening............")
                except sr.WaitTimeoutError:
                    # If no speech is detected within the timeout, print a message and continue listening for the wake word
                    respond("No audio detected. Listening for wake word again...")
                    continue  # Skip the rest of the loop and go back to listening for the wake word
                    
            try:
                
                respond("Let me think about it.")

                
                # Use Google's speech recognition to convert the audio to text
                text = r.recognize_google(audio)
                print("You said: " + text)

                
                log_to_file("You said: " + text)

                # Add a short response
                short_response = "think step by step and Answer in 1 sentence or less keep the response short " + text
                print(short_response)
                
                # Generate a completion using the model and the prompt
                completion = client.completions.create(model='gpt-3.5-turbo', prompt=short_response, max_tokens=100)
                
                # Extract the text from the completion response
                response_text = completion.choices[0].text.strip()
                print(response_text)



                # print(type(response))
                # if isinstance(response, dict):
                #     print(response.keys())
                # else:
                #     print(dir(response))


                # Speak the text
                # print(f"Response is {response_text}")
                # respond(response_text)

            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))

def main():
    think()

if __name__ == '__main__':
    main()
