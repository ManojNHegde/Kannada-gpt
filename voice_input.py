import speech_recognition as sr
from deep_translator import GoogleTranslator

def get_kannada_voice_input():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        # print("🎙️ Speak in Kannada...")
        audio = recognizer.listen(source)

        try:
            # Kannada Speech-to-Text
            kannada_text = recognizer.recognize_google(audio, language="kn-IN")
            # print(f"📝 Kannada Text: {kannada_text}")

            # Translate Kannada → English
            english_text = GoogleTranslator(source='kn', target='en').translate(kannada_text)
            # print(f"🌐 English Translation: {english_text}")

            return english_text, kannada_text
        except sr.UnknownValueError:
            print("⚠️ Could not understand audio.")
        except sr.RequestError:
            print("❌ API request error. Check your internet.")
    
    return None, None
