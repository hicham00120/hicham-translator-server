from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from google import genai
from google.genai import types
import os

app = FastAPI(title="HICHAM TRANSLATOR API")

@app.get("/")
def home():
    return {"status": "online"}

@app.post("/translate")
async def translate_audio(audio: UploadFile = File(...)):
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return JSONResponse(status_code=200, content={"success": True, "text": "⚠️ مفتاح API مفقود"})

        audio_data = await audio.read()
        if not audio_data:
            return JSONResponse(status_code=200, content={"success": True, "text": "⚠️ لا توجد بيانات صوتية"})

        client = genai.Client(api_key=api_key)
        audio_part = types.Part.from_bytes(data=audio_data, mime_type="audio/wav")

        prompt = (
            "Translate what is spoken in this audio directly into Algerian Darija (Arabic script). "
            "Output ONLY the translated words. If it is only music or noise, write: (موسيقى)"
        )

        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[audio_part, prompt],
            config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=80
            )
        )

        text = (response.text or "").strip()
        if not text:
            text = "(صوت غير مفهوم)"

        return JSONResponse(status_code=200, content={"success": True, "text": text})

    except Exception as e:
        error_msg = str(e)
        print("ERROR:", error_msg)
        return JSONResponse(status_code=200, content={"success": True, "text": f"⚠️ {error_msg[:60]}"})
