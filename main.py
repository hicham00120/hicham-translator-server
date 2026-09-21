from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from google import genai
from google.genai import types
import os

app = FastAPI(
    title="HICHAM TRANSLATOR API",
    version="2.1.5"
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
                content={"success": False, "error": "No API Key"}
            )

        audio_data = await audio.read()
        if not audio_data or len(audio_data) < 2000:
            return JSONResponse(
                status_code=200,
                content={"success": True, "text": ""}
            )

        client = genai.Client(api_key=api_key)

        audio_part = types.Part.from_bytes(
            data=audio_data,
            mime_type="audio/wav"
        )

        # برومت فائق السرعة ومباشر للترجمة اللحظية بالدارجة
        prompt = (
            "Live subtitle mode: Translate spoken English to Algerian Darija (Arabic letters). "
            "Output ONLY the translated words. No intro, no explanations. "
            "If silence, noise, or music, return completely empty."
        )

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=[audio_part, prompt],
            config=types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=60
            )
        )

        text = (response.text or "").strip()

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "text": text
            }
        )

    except Exception as e:
        return JSONResponse(
            status_code=200,
            content={
                "success": False,
                "text": ""
            }
        )
