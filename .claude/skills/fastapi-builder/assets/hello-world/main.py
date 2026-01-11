from fastapi import FastAPI

app = FastAPI(
    title="Hello World API",
    description="A simple FastAPI application",
    version="1.0.0"
)


@app.get("/")
def hello_world():
    return {"message": "Hello World"}

