from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from google import genai
from google.genai import types
import os

app = FastAPI(title="HICHAM TRANSLATOR API", version="2.2.2")

@app.get("/")
def home():
    return {"status": "online"}

@app.post("/translate")
async def translate_audio(audio: UploadFile = File(...)):
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return JSONResponse(status_code=200, content={"success": True, "text": "⚠️ GEMINI_API_KEY مفقود"})

        audio_data = await audio.read()
        # تجاهل الملفات الصوتية الصغيرة جداً (أقل من 0.5 ثانية تقريباً) لتوفير الكوتة
        if not audio_data or len(audio_data) < 2000:
            return JSONResponse(status_code=200, content={"success": True, "text": ""})

        client = genai.Client(api_key=api_key)
        audio_part = types.Part.from_bytes(data=audio_data, mime_type="audio/wav")

        # البرومت المعدل ليجبره يترجم أي حاجة يسمعها حتى لو مقطوعة
        prompt = (
            "Translate this short audio clip to Algerian Darija (Arabic script). "
            "Even if the audio is short or a word is cut off, translate whatever you hear directly. "
            "Translate strictly what is said."
            "Output only the translation."
        )

        # الموديل المجاني والسريع جداً والمستقر
        model_name = "gemini-1.5-flash"

        try:
            response = client.models.generate_content(
                model=model_name,
                contents=[audio_part, prompt],
                # إعدادات لتقليل وقت التفكير والحصول على جواب أسرع
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=70
                )
            )
            text = (response.text or "").strip()
            
            # إذا الصوت كان صمت تام
            if not text:
                return JSONResponse(status_code=200, content={"success": True, "text": "🎧 (صوت غير واضح)"})

            return JSONResponse(
                status_code=200,
                content={"success": True, "text": text}
            )

        except Exception as err:
            error_message = str(err)
            print(f"Error with {model_name}: {error_message}")
            
            # إذا كملت الكوتة اليومية (1500 طلب)، يظهر هذا التنبيه
            if "429" in error_message or "RESOURCE_EXHAUSTED" in error_message:
                return JSONResponse(status_code=200, content={"success": True, "text": "⚠️ (الحصة اليومية نفدت)"})
            
            # إذا كان خطأ آخر، نظهروه في الشاشة باش نعرفوه
            return JSONResponse(status_code=200, content={"success": True, "text": f"⚠️ {error_message[:70]}"})

    except Exception as e:
        system_error = str(e)
        print("SYSTEM ERROR:", system_error)
        return JSONResponse(
            status_code=200, 
            content={"success": True, "text": f"⚠️ سيرفر: {system_error[:50]}"}
        )
