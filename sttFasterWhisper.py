# https://www.youtube.com/watch?v=Mfbei9I8qQc - You won't believe how fast it is | Raspberry Pi Speech-to-Text
# https://github.com/SYSTRAN/faster-whisper/blob/master/tests/conftest.py


# https://gist.github.com/AIWintermuteAI/c916fbef719c58d89b1d69a4dd42eadf -- code below is from this link


# working code below
from faster_whisper import WhisperModel, decode_audio

audio_file = "audioFile/amr.mp3"
model_size = "tiny"
model = WhisperModel(model_size,compute_type="int8")
segments, info = model.transcribe(audio_file, beam_size=5)


# Print the transcription
# for segment in segments:
#     print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))




# Create a text file with the same name as the audio file
text_file = audio_file.rsplit('.', 1)[0] + '.txt'

with open(text_file, 'w') as f:
    for segment in segments:
        f.write("[%.2fs -> %.2fs] %s\n" % (segment.start, segment.end, segment.text))

print(f"Transcription written to {text_file}")