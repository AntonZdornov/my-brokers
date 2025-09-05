from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello, Anton!"}


@app.get("/health")
async def health():
    return {"status": "ok"}
