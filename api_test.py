"""Minimal test API"""
from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok", "message": "test works"}

@app.get("/test")
def test():
    return {"test": "passed"}

handler = Mangum(app)
