def main() -> None:
    import uvicorn
    uvicorn.run("app.main:app", reload=True)
