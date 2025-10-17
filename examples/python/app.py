from fastapi import FastAPI
import os

app = FastAPI(title="Dprod Python Example")

@app.get("/")
async def root():
    return {
        "message": "Hello from Dprod!",
        "service": "Python Example",
        "timestamp": "2024-01-01T00:00:00Z"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
