# backend/server.py

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
import subprocess
import os
import asyncio
import shutil
import glob
import zipfile
import datetime


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class BuildRequest(BaseModel):
    idea: str
    stream: bool


@app.get("/list_apps")
async def list_apps():
    base_folder = os.path.join(os.getcwd(), "../")
    apps = []

    for entry in os.listdir(base_folder):
        full_path = os.path.join(base_folder, entry)
        if (
            os.path.isdir(full_path)
            and not entry.startswith(".")
            and entry not in ["backend", "env", "node_modules", "__pycache__"]
            and os.path.isfile(os.path.join(full_path, "requirements.txt"))
        ):
            # Get creation time
            created_ts = os.path.getctime(full_path)
            created_time = datetime.datetime.fromtimestamp(created_ts).strftime("%Y-%m-%d %H:%M:%S")
            apps.append({"name": entry, "created": created_time})

    return {"apps": sorted(apps, key=lambda x: x["created"], reverse=True)}



@app.delete("/delete_app/{app_name}")
async def delete_app(app_name: str):
    base_folder = os.path.join(os.getcwd(), "../")
    target_path = os.path.join(base_folder, app_name)

    if not os.path.isdir(target_path):
        raise HTTPException(status_code=404, detail="App not found")

    shutil.rmtree(target_path)  # Delete entire app folder

    return {"success": True}


@app.get("/download_app/{app_name}")
async def download_app(app_name: str):
    base_folder = os.path.join(os.getcwd(), "../")
    app_folder = os.path.join(base_folder, app_name)

    if not os.path.isdir(app_folder):
        raise HTTPException(status_code=404, detail="App not found")

    zip_path = os.path.join(base_folder, f"{app_name}.zip")

    # Create a zip of the app
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(app_folder):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, app_folder)
                zipf.write(file_path, arcname)

    return FileResponse(zip_path, filename=f"{app_name}.zip", media_type="application/zip")


@app.post("/generate_app/stream")
async def generate_app_stream(request: Request):
    form = await request.json()
    idea = form.get("idea")
    stream = form.get("stream")
    project_name = form.get("projectName", "VibeApp")  # default fallback

    print(f"🛠️ Received idea: {idea}, Stream: {stream}")

    async def run_builder():
        process = await asyncio.create_subprocess_exec(
            "python", "main.py", idea, str(stream), project_name,
            cwd=os.path.join(os.getcwd(), "../"),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )

        while True:
            line = await process.stdout.readline()
            if not line:
                break
            decoded_line = line.decode()

            # FILTER OUT LibreSSL warnings
            if "NotOpenSSLWarning" in decoded_line:
                continue

            yield decoded_line

        await process.wait()


    return StreamingResponse(run_builder(), media_type="text/plain")
