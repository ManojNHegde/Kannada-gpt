from deep_translator import GoogleTranslator

def translate_en_to_kn(text):
    try:
        return GoogleTranslator(source='en', target='kn').translate(text)
    except Exception as e:
        print("❌ Translation failed:", e)
        return None
