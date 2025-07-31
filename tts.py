import os
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play

def speak_kannada(text, speed=1.25):
    try:
        if not text.strip():
            print("⚠️ Empty input to TTS")
            return

        # Generate MP3 using Google TTS
        tts = gTTS(text=text, lang='kn')
        file_name = "output.mp3"
        tts.save(file_name)

        # Load the MP3 file
        sound = AudioSegment.from_file(file_name)

        # Adjust playback speed
        faster_sound = sound._spawn(sound.raw_data, overrides={
            "frame_rate": int(sound.frame_rate * speed)
        }).set_frame_rate(sound.frame_rate)

        play(faster_sound)
        os.remove(file_name)

    except Exception as e:
        print("❌ Error using gTTS:", e)

