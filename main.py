from fastapi import FastAPI

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
