from fastapi import FastAPI

app = FastAPI(title="messages-s12")


@app.get("/")
def read_root() -> dict[str, str]:
    return {"status": "ok"}

