from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from openai import OpenAI
import os

app = FastAPI(
    title="HICHAM TRANSLATOR API",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "status": "online",
        "service": "HICHAM TRANSLATOR"
    }


@app.post("/translate")
async def translate_audio(
    audio: UploadFile = File(...)
):
    try:
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": "OPENAI_API_KEY غير موجود في Render"
                }
            )

        client = OpenAI(api_key=api_key)

        audio_data = await audio.read()

        if not audio_data:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": "ملف الصوت فارغ"
                }
            )

        transcription = client.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe",
            file=(
                audio.filename or "audio.m4a",
                audio_data,
                audio.content_type or "audio/m4a"
            )
        )

        text = transcription.text

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