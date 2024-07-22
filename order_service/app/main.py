from fastapi import FastAPI

app = FastAPI()

@app.get("/") 
def root():  
    return {"messages": "Purchase/Order Services"}