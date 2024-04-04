from model import llm_processor
import shutil
from uuid import uuid4
import os

from pydantic import BaseModel
from typing import Any

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


class Response(BaseModel):
    result: str | None


origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
    "http://122.165.141.89:8888",
]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PredictBody(BaseModel):
    query: str
    filename: str


@app.post("/predict")
async def predict(req: PredictBody) -> Any:
    result = llm_processor(
        f"{UPLOAD_DIR}/{req.filename}", req.filename.split(".")[-1], req.query)
    result = "".join(result.split("Answer:")[1:])
    return {"result": result}


@app.post("/upload")
async def upload(file: UploadFile = File()):
    filetype = file.filename.split(".")[-1]
    filename = f"{uuid4()}.{filetype}"
    with open(f"{UPLOAD_DIR}/{filename}", "wb") as newfile:
        shutil.copyfileobj(file.file, newfile)
    return {"message": "ok", "filename": filename, "filetype": filetype}
