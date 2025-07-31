import streamlit as st
import sounddevice as sd
import numpy as np
import speech_recognition as sr
from deep_translator import GoogleTranslator

DURATION = 5  # seconds

def record_audio(duration=DURATION, fs=16000):
    # st.info("🎤 Listening... Please speak now.")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    return audio.flatten(), fs

def recognize_kannada(audio_np, fs):
    recognizer = sr.Recognizer()
    audio_data = sr.AudioData(audio_np.tobytes(), fs, 2)
    try:
        text = recognizer.recognize_google(audio_data, language="kn-IN")
        return text
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        return f"API Error: {e}"

def get_kannada_voice_input():
    audio_np, fs = record_audio()
    kannada_text = recognize_kannada(audio_np, fs)
    english_text = ""
    if kannada_text:
        english_text = GoogleTranslator(source='kn', target='en').translate(kannada_text)
    return english_text, kannada_text
