from langchain_community.llms import Ollama
import pyttsx3
import speech_recognition as sr

# Initialize the Ollama model
model = "tinyllama"
llm = Ollama(model=model)

# Initialize the Speech to Text engine
engine = pyttsx3.init()

# Create a recognizer object for Automatic Speech Recognition
r = sr.Recognizer()

# Use the microphone as the audio source
with sr.Microphone() as source:
    print("Listening...")
    audio = r.listen(source)

try:
    # Use Google's speech recognition to convert the audio to text
    text = r.recognize_google(audio)
    print("You said: " + text)

    # Ask the llm the message
    response = llm.invoke(text)
    print(f"Response is {response}")

    # Speak the text
    engine.say(response)
    engine.runAndWait()

except sr.UnknownValueError:
    print("Google Speech Recognition could not understand audio")
except sr.RequestError as e:
    print("Could not request results from Google Speech Recognition service; {0}".format(e))