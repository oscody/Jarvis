
# Automatic Speech Recognition

import speech_recognition as sr

# create a recognizer object
r = sr.Recognizer()

# use the microphone as the audio source
with sr.Microphone() as source:
    print("Listening...")
    audio = r.listen(source)

try:
    # use google's speech recognition to convert the audio to text
    text = r.recognize_google(audio)
    print("You said: " + text)
except sr.UnknownValueError:
    print("Google Speech Recognition could not understand audio")
except sr.RequestError as e:
    print("Could not request results from Google Speech Recognition service; {0}".format(e))