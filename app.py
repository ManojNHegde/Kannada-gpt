import streamlit as st
import time
from voice_input import get_kannada_voice_input
from qa_chain import ask_llama
from translator import translate_en_to_kn
from tts import speak_kannada

st.set_page_config(page_title="ಕನ್ನಡ ಚಾಟ್‌ಬಾಟ್", layout="centered")

# Initialize session state
if "chat" not in st.session_state:
    st.session_state.chat = []
if "chat_active" not in st.session_state:
    st.session_state.chat_active = False

st.title("🗣️ ಕನ್ನಡ ಚಾಟ್‌ಬಾಟ್")

# Start / Stop controls
col1, col2 = st.columns([1, 1])
with col1:
    if not st.session_state.chat_active:
        if st.button("▶️ ಸಂಭಾಷಣೆ ಪ್ರಾರಂಭಿಸಿ"):
            st.session_state.chat_active = True
with col2:
    if st.session_state.chat_active:
        if st.button("⏹️ ನಿಲ್ಲಿಸಿ"):
            st.session_state.chat_active = False

# Show chat history
for sender, message in st.session_state.chat:
    with st.chat_message(sender):
        st.markdown(message)

# Chat loop
if st.session_state.chat_active:
    st.markdown("🎙️ **ಧ್ವನಿ ಶ್ರವಣ ನಡೆಯುತ್ತಿದೆ...** (ನಿಲ್ಲಿಸಲು ಮೇಲಿನ ಬಟನ್ ಒತ್ತಿ)")
    placeholder = st.empty()

    while st.session_state.chat_active:
        with placeholder.container():
            st.markdown("🟢 ಧ್ವನಿ ಕೇಳಲಾಗುತ್ತಿದೆ...")

        try:
            en_text, kn_text = get_kannada_voice_input()
        except Exception as e:
            st.warning(f"🎤 ಧ್ವನಿ ಪಡೆಯಲು ದೋಷ: {e}")
            continue

        if not st.session_state.chat_active:
            break

        if en_text and kn_text:
            with placeholder.container():
                st.markdown("🤖 ಯೋಚಿಸುತ್ತಿದೆ...")

            # Ask LLM and get Kannada response
            llm_response_en = ask_llama(en_text)
            kn_response = translate_en_to_kn(llm_response_en)

            # Speak in Kannada
            speak_kannada(kn_response)

            # Save chat history
            st.session_state.chat.append(("🙋‍♂️", kn_text))
            st.session_state.chat.append(("🤖", kn_response))

        else:
            st.warning("⚠️ ಧ್ವನಿಯನ್ನು ಪತ್ತೆಮಾಡಲಾಗಲಿಲ್ಲ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.")

        time.sleep(1)
        st.rerun()
