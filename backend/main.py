from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
import subprocess
import traceback
import speech_recognition as sr
from gtts import gTTS
from qa_chain import ask_llama  # Your custom QA function
from translator import translate_en_to_kn  # English to Kannada translation

app = FastAPI()

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories
UPLOAD_DIR = "uploads"
AUDIO_OUT_DIR = "static/audio"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(AUDIO_OUT_DIR, exist_ok=True)
print("Hi startes")
@app.post("/voice")
async def handle_voice(file: UploadFile = File(...)):
    try:
        # Step 1: Save uploaded audio
        ext = file.filename.split('.')[-1]
        file_id = str(uuid.uuid4())
        input_path = os.path.join(UPLOAD_DIR, f"{file_id}.{ext}")
        print(f"[UPLOAD] Saving file as: {input_path}")
        with open(input_path, "wb") as f:
            f.write(await file.read())

        # Step 2: Convert to WAV if needed
        if not input_path.endswith(".wav"):
            wav_path = input_path.replace(f".{ext}", ".wav")
            print(f"[CONVERT] Converting to WAV: {wav_path}")
            subprocess.run(["ffmpeg", "-i", input_path, wav_path, "-y"], check=True)
        else:
            wav_path = input_path
        print("[CONVERT] Conversion done.")

        # Step 3: Kannada Speech Recognition
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            print("[SPEECH] Performing recognition...")
            user_text = recognizer.recognize_google(audio_data, language="kn-IN")
        print(f"[SPEECH] User said: {user_text}")

        # Step 4: LLM Response
        print("[LLM] Sending to LLaMA/LLM...")
        bot_reply = ask_llama(user_text)
        print(f"[LLM] English reply: {bot_reply}")

        # Step 5: Translate to Kannada
        print("[TRANSLATE] Translating to Kannada...")
        kannada_reply = translate_en_to_kn(bot_reply)
        print(f"[TRANSLATE] Kannada reply: {kannada_reply}")

        # Step 6: Convert Kannada text to audio
        output_audio_path = os.path.join(AUDIO_OUT_DIR, f"{file_id}.mp3")
        tts = gTTS(kannada_reply, lang='kn')
        tts.save(output_audio_path)
        print(f"[AUDIO] Saved to: {output_audio_path}")

        return JSONResponse({
            "user_text": user_text,
            "bot_text": kannada_reply,
            "audio_url": f"http://localhost:8000/static/audio/{file_id}.mp3"
        })

    except sr.UnknownValueError:
        print("[ERROR] Could not understand audio.")
        return JSONResponse({"error": "Could not understand the audio."}, status_code=400)
    except subprocess.CalledProcessError:
        print("[ERROR] Audio conversion failed.")
        return JSONResponse({"error": "Audio conversion failed."}, status_code=500)
    except Exception as e:
        print("[ERROR] Exception occurred:")
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/clear_chat")
async def clear_chat():
    try:
        file_path = "conversation_history.txt"
        # Clear contents if file exists
        if os.path.exists(file_path):
            open(file_path, 'w').close()
            print("[CLEAR] conversation_history.txt cleared.")
            return JSONResponse({"message": "Chat history cleared successfully."})
        else:
            print("[CLEAR] File does not exist. Nothing to clear.")
            return JSONResponse({"message": "File not found. Nothing to clear."}, status_code=404)
    except Exception as e:
        print(f"[ERROR] Failed to clear chat history: {str(e)}")
        return JSONResponse({"error": "Failed to clear chat history."}, status_code=500)


@app.get("/static/audio/{filename}")
async def get_audio(filename: str):
    path = os.path.join(AUDIO_OUT_DIR, filename)
    if not os.path.exists(path):
        print(f"[404] Audio file not found: {filename}")
        return JSONResponse({"error": "File not found"}, status_code=404)
    print(f"[200] Serving audio file: {filename}")
    return FileResponse(path)
