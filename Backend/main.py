from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "FastAPI backend is running 🚀"}

@app.get("/chat")
def chat_example():
    return {"response": "This is where chat logic will go"}
