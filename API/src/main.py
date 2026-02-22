from fastapi import FastAPI

app = FastAPI(title="C4476 Project API")

@app.get("/")
def hello_world():
    return {"Hello":"World"}
