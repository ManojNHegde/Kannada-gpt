import gradio as gr
from backend.voice_input import get_kannada_voice_input
from qa_chain import ask_llama
from backend.translator import translate_en_to_kn
from backend.tts import speak_kannada

def process_audio(audio_file, chat_history):
    en_text, kn_text = get_kannada_voice_input(audio_file)

    if not en_text or not kn_text:
        chat_history.append({"role": "user", "content": "⚠️ ಧ್ವನಿಯನ್ನು ಗುರುತಿಸಲಾಗಿಲ್ಲ."})
        return chat_history, None

    llm_response_en = ask_llama(en_text)
    kn_response = translate_en_to_kn(llm_response_en)
    tts_audio_path = speak_kannada(kn_response)

    chat_history.append({"role": "user", "content": kn_text})
    chat_history.append({"role": "assistant", "content": kn_response})

    return chat_history, tts_audio_path

with gr.Blocks() as demo:
    gr.Markdown("## 🗣️ ಕನ್ನಡ ಧ್ವನಿ ಚಾಟ್‌ಬಾಟ್")
    chatbot = gr.Chatbot(label="💬 ಸಂಭಾಷಣೆ", type="messages")
    audio_input = gr.Audio(sources=["microphone"], type="filepath", format="mp3", label="🎤 ಧ್ವನಿ ನಮೂದಿಸಿ")
    output_audio = gr.Audio(label="🔊 ಸ್ಪೀಚ್ ಔಟ್‌ಪುಟ್")
    btn = gr.Button("📤 ಕಳುಹಿಸಿ")
    state = gr.State([])

    btn.click(fn=process_audio, inputs=[audio_input, state], outputs=[chatbot, output_audio])

demo.launch()
