from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from google import genai
from google.genai import types
import os

app = FastAPI(
    title="HICHAM TRANSLATOR API",
    version="2.1.2"
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
        # 1. التحقق من مفتاح الـ API
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": "GEMINI_API_KEY غير موجود في إعدادات Render"
                }
            )

        # 2. قراءة بيانات الصوت مباشرة في الذاكرة
        audio_data = await audio.read()
        if not audio_data:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": "ملف الصوت فارغ"
                }
            )

        # 3. إعداد عميل Gemini
        client = genai.Client(api_key=api_key)

        # 4. تجهيز الصوت كبيانات بايت مباشرة
        audio_part = types.Part.from_bytes(
            data=audio_data,
            mime_type="audio/wav"
        )

        prompt = (
            "Listen to this audio chunk from a video. "
            "Translate what is spoken directly into Algerian Darija (using Arabic script). "
            "Keep it natural and concise. If there is only background noise or music with no clear speech, return nothing."
        )

        # 5. استدعاء الموديل المحدث والمطلوب
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=[audio_part, prompt]
        )

        text = (response.text or "").strip()
        print("Gemini transcription (Darija):", text)

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "filename": audio.filename or "audio.wav",
                "size_bytes": len(audio_data),
                "text": text
            }
        )

    except Exception as e:
        error_message = str(e)
        print("GEMINI ERROR:", error_message)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": error_message
            }
        )
