from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from google import genai
from google.genai import types
import os

app = FastAPI(
    title="HICHAM TRANSLATOR API",
    version="2.1.6"
)

@app.get("/")
def home():
    return {"status": "online"}

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
                content={"success": False, "error": "GEMINI_API_KEY مفقود في Render"}
            )

        audio_data = await audio.read()
        if not audio_data or len(audio_data) == 0:
            return JSONResponse(
                status_code=200,
                content={"success": True, "text": ""}
            )

        client = genai.Client(api_key=api_key)

        audio_part = types.Part.from_bytes(
            data=audio_data,
            mime_type="audio/wav"
        )

        prompt = (
            "Translate any spoken speech in this short video clip directly into Algerian Darija (Arabic script). "
            "Output ONLY the translated words. If there is no clear speech, return nothing."
        )

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=[audio_part, prompt],
            config=types.GenerateContentConfig(
                temperature=0.2
            )
        )

        text = (response.text or "").strip()
        print("Gemini result:", text)

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "text": text
            }
        )

    except Exception as e:
        print("GEMINI ERROR:", str(e))
        return JSONResponse(
            status_code=200,
            content={
                "success": False,
                "error": str(e),
                "text": ""
            }
        )
