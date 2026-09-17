from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse

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
        audio_data = await audio.read()

        return JSONResponse(
            {
                "success": True,
                "filename": audio.filename,
                "content_type": audio.content_type,
                "size_bytes": len(audio_data),
                "message": "تم استقبال الصوت بنجاح"
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
