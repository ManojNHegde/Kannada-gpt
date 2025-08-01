import streamlit as st
from backend.voice_input import start_audio_stream, get_kannada_voice_input
import time

st.title("🎙️ Kannada Voice Input Test")

ctx = start_audio_stream()

if ctx and ctx.state.playing:
    st.success("✅ Audio stream started. Speak now...")

    with st.spinner("🔴 Listening for 6 seconds..."):
        time.sleep(6)  # Wait while you speak
        en_text, kn_text = get_kannada_voice_input()

    if kn_text:
        st.success(f"🗣️ Kannada Recognized: {kn_text}")
        st.info(f"🌐 Translated to English: {en_text}")
    else:
        st.warning("⚠️ ಧ್ವನಿಯನ್ನು ಗುರುತಿಸಲಾಗಲಿಲ್ಲ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.")
else:
    st.warning("❌ Audio stream not active.")
