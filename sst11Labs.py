# import os
# from elevenlabs.client import ElevenLabs
# from elevenlabs.types.voice_response import VoiceResponse


# print(os.getenv('elevenlabs'))
# ELEVENLABS = os.getenv('elevenlabs')


#     # Test that we can get a voice from id
# voice_id = "21m00Tcm4TlvDq8ikWAM"

# client = ElevenLabs()
# voice = client.voices.get(voice_id)


# # # client = ElevenLabs(api_key=ELEVENLABS)

# # from elevenlabs import voices, generate

# # voices = voices()
# # audio = generate(text="Hello there!", voice=voices[0])
# # print(voices)

# from ElevenLabs.client import ElevenLabs

# # Create a client
# client = ElevenLabs.Client(api_key=ELEVENLABS)

# # Generate audio from text
# audio = client.generate_audio(text="Hello, world!")

# # Save the audio to a file
# with open("hello_world.mp3", "wb") as f:
#     f.write(audio)


from elevenlabs import generate, voices, Voice, VoiceSettings, play, stream

audio = generate(
        text="Hello! My name is Bella.",
        voice=Voice(
            voice_id='EXAVITQu4vr4xnSDxMaL',
            settings=VoiceSettings(stability=0.71, similarity_boost=0.5, style=0.0, use_speaker_boost=True)
        )
)

play(audio)