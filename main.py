from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from google import genai
from google.genai import types
import os

app = FastAPI(
    title="HICHAM TRANSLATOR API",
    version="2.1.3"
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
        if not audio_data:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": "ملف الصوت فارغ"
                }
            )

        client = genai.Client(api_key=api_key)

        audio_part = types.Part.from_bytes(
            data=audio_data,
            mime_type="audio/wav"
        )

        prompt = (
            "Translate this short audio clip immediately into Algerian Darija (Arabic script). "
            "Output ONLY the translated spoken words concisely. "
            "If it is silence, noise, or music, return an empty response."
        )

        # تجربة الموديل الموصى به أولاً، ثم الموديل الاحتياطي
        models_to_try = ["gemini-3.6-flash", "gemini-2.5-flash", "gemini-1.5-flash"]
        response_text = ""
        last_error = None

        for model_name in models_to_try:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=[audio_part, prompt]
                )
                response_text = (response.text or "").strip()
                break
            except Exception as ex:
                last_error = str(ex)
                continue

        if not response_text and last_error and "404" in last_error:
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": f"Model error: {last_error}"
                }
            )

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "filename": audio.filename or "audio.wav",
                "size_bytes": len(audio_data),
                "text": response_text
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
