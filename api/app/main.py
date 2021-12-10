from typing import Optional
from fastapi import FastAPI
import requests
app = FastAPI()

@app.on_event("startup")
def startup():
    pass

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/rec/{handle}")
def get_recommend(handle: str):
    return {"Hello": "World"}