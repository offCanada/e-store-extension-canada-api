from fastapi import FastAPI

app = FastAPI(title="E-Store Extension Canada API")

@app.get("/")
def root():
    return {"status": "ok"}