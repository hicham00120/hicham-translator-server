from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from google import genai
from google.genai import types
import os

app = FastAPI(
    title="HICHAM TRANSLATOR API",
    version="2.1.4"
)

@app.get("/")
def home():
    return {
        "status": "online",
        "service": "HICHAM TRANSLATOR",
        "engine": "Google Gemini"
    }

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/translate")
async def translate_audio(audio: UploadFile = File(...)):
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": "GEMINI_API_KEY غير موجود في إعدادات Render"
                }
            )

        audio_data = await audio.read()
        if not audio_data or len(audio_data) < 1000:
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "text": ""
                }
            )

        client = genai.Client(api_key=api_key)

        audio_part = types.Part.from_bytes(
            data=audio_data,
            mime_type="audio/wav"
        )

        prompt = (
            "You are a real-time translator. "
            "Translate any spoken English speech in this audio immediately into concise Algerian Darija (in Arabic alphabet). "
            "Translate strictly what is said. If there is no speech, silence, or just music, reply with nothing."
        )

        # الموديل الموصى به
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=[audio_part, prompt]
        )

        text = (response.text or "").strip()
        print("Translated:", text)

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "text": text
            }
        )

    except Exception as e:
        error_message = str(e)
        print("GEMINI ERROR:", error_message)
        
        # تجنب إرجاع 500 لإبقاء التطبيق شغال بسلاسة
        return JSONResponse(
            status_code=200,
            content={
                "success": False,
                "error": error_message,
                "text": ""
            }
        )
