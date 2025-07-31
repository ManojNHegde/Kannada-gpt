# voice_input.py

import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, ClientSettings
import av
import speech_recognition as sr
import numpy as np
from deep_translator import GoogleTranslator

# For client settings (required to avoid browser errors)
WEBRTC_CLIENT_SETTINGS = ClientSettings(
    rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
    media_stream_constraints={"audio": True, "video": False},
)

class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.audio_chunks = []

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        pcm = frame.to_ndarray()
        self.audio_chunks.append(pcm)
        return frame

def get_kannada_voice_input():
    ctx = webrtc_streamer(
        key="speech",
        mode="SENDRECV",
        in_audio=True,
        client_settings=WEBRTC_CLIENT_SETTINGS,
        audio_processor_factory=AudioProcessor,
        async_processing=True,
    )

    if ctx.audio_processor and ctx.audio_processor.audio_chunks:
        audio = np.concatenate(ctx.audio_processor.audio_chunks, axis=0)
        audio_bytes = audio.tobytes()
        recognizer = sr.Recognizer()
        audio_data = sr.AudioData(audio_bytes, 16000, 2)

        try:
            kannada_text = recognizer.recognize_google(audio_data, language="kn-IN")
            english_text = GoogleTranslator(source='kn', target='en').translate(kannada_text)
            return english_text, kannada_text
        except sr.UnknownValueError:
            st.warning("⚠️ ಧ್ವನಿಯನ್ನು ಗುರುತಿಸಲಾಗಲಿಲ್ಲ.")
        except sr.RequestError as e:
            st.error(f"Google Speech API ದೋಷ: {e}")
    
    return "", ""
