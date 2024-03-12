# stt: Speech to Text

import pyttsx3

engine = pyttsx3.init()  # Initialize the converter
engine.say("Hello, world!")  # Add text to the speech queue
engine.runAndWait()  # Process the speech queue and play the audio
