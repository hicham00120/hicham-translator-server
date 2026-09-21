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
            "Translate this short English audio directly into Algerian Darija (Arabic script). "
            "Output ONLY the translated words. If it is only music or noise, return (موسيقى)"
        )

        # استخراج الموديل المتاح في حسابك تلقائياً لتفادي أي خطأ 404
        selected_model = None
        try:
            for m in client.models.list():
                m_name = getattr(m, "name", "")
                if "flash" in m_name.lower():
                    selected_model = m_name
                    break
        except Exception:
            pass

        # إذا تعذر الفحص نعتمد الموديل القياسي الأكثر توفراً
        if not selected_model:
            selected_model = "gemini-2.5-flash"

        response = client.models.generate_content(
            model=selected_model,
            contents=[audio_part, prompt],
            config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=70
            )
        )

        text = (response.text or "").strip()
        if not text:
            text = "(صوت غير مفهوم)"

        return JSONResponse(status_code=200, content={"success": True, "text": text})

    except Exception as e:
        err = str(e)
        print("API ERROR:", err)
        return JSONResponse(status_code=200, content={"success": True, "text": f"⚠️ {err[:65]}"})
