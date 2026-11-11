from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
"""
from collections import deque
import json
import random
import os
"""

app = FastAPI()

@app.get("/message")
async def root():
    return {"message": "Hello World"}

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")