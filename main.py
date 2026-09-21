from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from google import genai
from google.genai import types
import os

app = FastAPI(
    title="HICHAM TRANSLATOR API",
    version="2.2.0"
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
                content={"success": False, "error": "GEMINI_API_KEY مفقود"}
            )

        audio_data = await audio.read()
        if not audio_data:
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
            "Translate this short English audio directly into concise Algerian Darija (Arabic letters). "
            "Output ONLY the translated speech. If silence, music, or unclear noise, output nothing."
        )

        # قائمة موديلات مجانية بحصص يومية كبيرة (تصل لـ 1500 طلب يومياً)
        models_pool = [
            "gemini-2.0-flash",
            "gemini-1.5-flash",
            "gemini-2.5-flash"
        ]

        text = ""
        last_error = ""

        for model_name in models_pool:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=[audio_part, prompt],
                    config=types.GenerateContentConfig(
                        temperature=0.1,
                        max_output_tokens=60
                    )
                )
                text = (response.text or "").strip()
                last_error = ""
                break
            except Exception as err:
                last_error = str(err)
                print(f"Error with {model_name}: {last_error}")
                continue

        if last_error and not text:
            # إذا استنفدت الحصة تماماً، نرجع نص فارغ باش ما نعطلوش الشاشة برسالة خطأ طويلة
            return JSONResponse(
                status_code=200,
                content={"success": True, "text": ""}
            )

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "text": text
            }
        )

    except Exception as e:
        print("SYSTEM ERROR:", str(e))
        return JSONResponse(
            status_code=200,
            content={"success": True, "text": ""}
        )
