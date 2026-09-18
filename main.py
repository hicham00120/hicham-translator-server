from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from google import genai
import os

app = FastAPI(
    title="HICHAM TRANSLATOR API",
    version="2.0.0"
)


@app.get("/")
def home():
    return {
        "status": "online",
        "service": "HICHAM TRANSLATOR",
        "engine": "Google Gemini"
    }


@app.post("/translate")
async def translate_audio(
    audio: UploadFile = File(...)
):
    try:
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": "GEMINI_API_KEY غير موجود في Render"
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

        uploaded_file = client.files.upload(
            file=audio_data,
            config={
                "mime_type": audio.content_type or "audio/mp4"
            }
        )

        response = client.models.generate_content(
            model="gemini-3.5-transcribe",
            contents=[
                uploaded_file,
                "Transcribe this audio exactly. Detect the spoken language automatically. Return only the transcription text."
            ]
        )

        text = response.text or ""

        return JSONResponse(
            {
                "success": True,
                "filename": audio.filename,
                "content_type": audio.content_type,
                "size_bytes": len(audio_data),
                "text": text
            }
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )