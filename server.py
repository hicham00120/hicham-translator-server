from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/")
def home():
    return {
        "status": "ok",
        "message": "HICHAM TRANSLATOR SERVER"
    }


@app.post("/audio")
async def receive_audio(file: UploadFile = File(...)):

    audio_data = await file.read()

    return JSONResponse({
        "status": "received",
        "filename": file.filename,
        "size": len(audio_data)
    })
