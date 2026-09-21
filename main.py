from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from google import genai
import os
import tempfile


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
    return {
        "status": "ok"
    }


@app.post("/translate")
async def translate_audio(
    audio: UploadFile = File(...)
):

    temp_path = None

    try:

        # =========================
        # 1. Check API Key
        # =========================

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:

            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": "GEMINI_API_KEY غير موجود في Render"
                }
            )

        # =========================
        # 2. Read audio
        # =========================

        audio_data = await audio.read()

        if not audio_data:

            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": "ملف الصوت فارغ"
                }
            )

        filename = audio.filename or "audio.wav"

        # التطبيق يرسل WAV
        extension = ".wav"

        # =========================
        # 3. Save temporary WAV
        # =========================

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=extension
        ) as temp_file:

            temp_file.write(audio_data)

            temp_path = temp_file.name

        # =========================
        # 4. Gemini client
        # =========================

        client = genai.Client(
            api_key=api_key
        )

        # =========================
        # 5. Upload file to Gemini
        # =========================

        uploaded_file = client.files.upload(
            file=temp_path
        )

        print(
            "Gemini uploaded file:",
            uploaded_file
        )

        print(
            "Gemini MIME:",
            getattr(
                uploaded_file,
                "mime_type",
                None
            )
        )

        # =========================
        # 6. Use MIME returned by Gemini
        # =========================

        gemini_mime =
            getattr(
                uploaded_file,
                "mime_type",
                None
            )

        if not gemini_mime:

            gemini_mime = "audio/wav"

        # =========================
        # 7. Transcription
        # =========================

        interaction = client.interactions.create(

            model="gemini-3.5-transcribe",

            input=[
                {
                    "type": "audio",

                    "uri": uploaded_file.uri,

                    "mime_type": gemini_mime
                }
            ]
        )

        # =========================
        # 8. Get text
        # =========================

        text = (
            interaction.output_text
            or ""
        ).strip()

        print(
            "Gemini transcription:",
            text
        )

        if not text:

            return JSONResponse(
                status_code=200,
                content={
                    "success": False,
                    "error": "Gemini رجع نص فارغ"
                }
            )

        # =========================
        # 9. Success
        # =========================

        return JSONResponse(

            status_code=200,

            content={

                "success": True,

                "filename": filename,

                "content_type": gemini_mime,

                "size_bytes": len(audio_data),

                "text": text
            }
        )

    except Exception as e:

        # مهم جداً:
        # نرجع الخطأ الحقيقي للتطبيق

        error_message = str(e)

        print(
            "GEMINI ERROR:",
            error_message
        )

        return JSONResponse(

            status_code=500,

            content={

                "success": False,

                "error": error_message
            }
        )

    finally:

        if temp_path and os.path.exists(temp_path):

            try:
                os.remove(temp_path)

            except Exception:
                pass
