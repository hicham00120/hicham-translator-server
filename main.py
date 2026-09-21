from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from google import genai
from google.genai import types
import os

app = FastAPI(title="HICHAM TRANSLATOR API", version="2.2.1")

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
        if not audio_data or len(audio_data) < 1000:
            return JSONResponse(status_code=200, content={"success": True, "text": ""})

        client = genai.Client(api_key=api_key)
        audio_part = types.Part.from_bytes(data=audio_data, mime_type="audio/wav")

        # برومت جديد يجبره يترجم أي حاجة يسمعها وما يتجاهلش الصوت القصير
        prompt = (
            "Translate this audio to Algerian Darija (Arabic script). "
            "Even if the audio is short or a word is cut off, translate whatever you hear directly. "
            "Output only the translation."
        )

        models_pool = ["gemini-2.0-flash", "gemini-1.5-flash"]
        text = ""
        last_error = ""

        for model_name in models_pool:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=[audio_part, prompt],
                    config=types.GenerateContentConfig(temperature=0.2)
                )
                text = (response.text or "").strip()
                last_error = ""
                break
            except Exception as err:
                last_error = str(err)
                continue

        # إذا كاين خطأ وما رجعش الترجمة، نظهرو الخطأ في الشاشة باش نعرفوه
        if last_error and not text:
            return JSONResponse(
                status_code=200, 
                content={"success": True, "text": f"⚠️ {last_error[:70]}"}
            )
        
        # إذا الصوت كان صمت تام
        if not text:
            return JSONResponse(
                status_code=200, 
                content={"success": True, "text": "🎧 (صوت غير واضح)"}
            )

        return JSONResponse(
            status_code=200,
            content={"success": True, "text": text}
        )

    except Exception as e:
        return JSONResponse(
            status_code=200, 
            content={"success": True, "text": f"⚠️ سيرفر: {str(e)[:50]}"}
        )
