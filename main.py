from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from google import genai
import os
import tempfile


app = FastAPI(
    title="HICHAM TRANSLATOR API",
    version="2.1.1"
)


MIME_TYPES = {
    ".m4a": "audio/mp4",
    ".mp4": "audio/mp4",
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".ogg": "audio/ogg",
    ".webm": "audio/webm",
}


@app.get("/")
def home():
    return {
        "status": "online",
        "service": "HICHAM TRANSLATOR",
        "engine": "Google Gemini"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.post("/translate")
async def translate_audio(
    audio: UploadFile = File(...)
):
    temp_path = None

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

        filename = audio.filename or "audio.m4a"
        extension = os.path.splitext(filename)[1].lower()

        if not extension:
            extension = ".m4a"

        mime_type = MIME_TYPES.get(
            extension,
            audio.content_type or "audio/mp4"
        )

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=extension
        ) as temp_file:
            temp_file.write(audio_data)
            temp_path = temp_file.name

        client = genai.Client(
            api_key=api_key
        )

        uploaded_file = client.files.upload(
            file=temp_path
        )

        interaction = client.interactions.create(
            model="gemini-3.5-transcribe",
            input=[
                {
                    "type": "audio",
                    "uri": uploaded_file.uri,
                    "mime_type": mime_type
                }
            ]
        )

        text = interaction.output_text or ""

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "filename": filename,
                "content_type": mime_type,
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

    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass