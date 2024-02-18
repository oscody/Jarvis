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
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate

load_dotenv()

llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")

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
            respond("I am listening.")

            with source as s:
                print("Listening.")
                r.adjust_for_ambient_noise(s)
                
                try:
                    # Wait for a question with a timeout (e.g., 5 seconds)
                    audio = r.listen(s, timeout=10)
                    print("Listening....")
                except sr.WaitTimeoutError:
                    # If no speech is detected within the timeout, print a message and continue listening for the wake word
                    respond("No audio detected. Try again.")
                    continue  # Skip the rest of the loop and go back to listening for the wake word
                    
            try:
                
                respond("Let me think about it.")

                
                # Use Google's speech recognition to convert the audio to text
                text = r.recognize_google(audio)
                print("You said: " + text)

                
                log_to_file("You said: " + text)

                summary_template = """
                given the text {text}:
                1. think step by step and answer in 1 sentence or less
                2. If you are not able ti determine the answer you you dont know
                3. Keep the response short
                """
                print(summary_template)

                summary_prompt_template = PromptTemplate(
                    input_variables=["text"], template=summary_template
                )


                chain = LLMChain(llm=llm, prompt=summary_prompt_template)
                res = chain.invoke(input={"text": text})

                # Assuming 'res' contains a key 'text' that holds the response text
                # You might need to adjust this based on the actual structure of 'res'
                response_text = res.get('text', 'Sorry, I could not process the response.') if isinstance(res, dict) else str(res)

                # Now, pass only the extracted text to 'respond'
                print(f"Response is {response_text}")
                respond(response_text)

            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))

def main():
    think()

if __name__ == '__main__':
    main()
