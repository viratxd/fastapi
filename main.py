from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import subprocess
import shutil
import zipfile
from typing import Optional
import uvicorn

app = FastAPI(title="APK File Processor")

# Mount static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")

# Ensure upload directory exists
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def debug_apk(input_path: str, output_dir: str) -> Optional[str]:
    command = f"apk-mitm {input_path} -o {output_dir}"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        output_file_name = result.stdout.split("Patched file: ")[-1].strip()
        return os.path.join(output_dir, output_file_name)
    return None

def process_xapk(xapk_path: str) -> Optional[str]:
    try:
        folder = os.path.dirname(xapk_path)
        name_without_ext = os.path.splitext(os.path.basename(xapk_path))[0]
        zip_path = os.path.join(folder, f"{name_without_ext}.zip")
        extract_dir = os.path.join(folder, name_without_ext)
        
        shutil.move(xapk_path, zip_path)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        os.remove(zip_path)
        command = f'java -jar APKEditor.jar m -i "{extract_dir}"'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            merged_apk_path = os.path.join(folder, f"{name_without_ext}_merged.apk")
            return process_sign(merged_apk_path)
        return None
    except Exception:
        shutil.rmtree(extract_dir, ignore_errors=True)
        return None

def process_sign(apk_path: str) -> Optional[str]:
    command = f"java -jar uber-apk-signer.jar --apks {apk_path}"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        signed_apk_path = apk_path.replace('.apk', '-aligned-debugSigned.apk')
        if os.path.exists(signed_apk_path):
            return signed_apk_path
    return None

def cleanup_files():
    shutil.rmtree(UPLOAD_DIR, ignore_errors=True)

@app.get("/", response_class=HTMLResponse)
async def read_root(request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/process/xapk")
async def process_xapk_file(file: UploadFile = File(...)):
    if not file.filename.endswith('.xapk'):
        raise HTTPException(status_code=400, detail="File must be an XAPK")
    file_path = os.path.join(UPLOAD_DIR, file.filename.replace(" ", "_"))
    with open(file_path, "wb") as f:
        f.write(await file.read())
    output_path = process_xapk(file_path)
    if output_path and os.path.exists(output_path):
        return FileResponse(output_path, filename=os.path.basename(output_path))
    cleanup_files()
    raise HTTPException(status_code=500, detail="Failed to process XAPK")

@app.post("/process/sign")
async def sign_apk_file(file: UploadFile = File(...)):
    if not file.filename.endswith('.apk'):
        raise HTTPException(status_code=400, detail="File must be an APK")
    file_path = os.path.join(UPLOAD_DIR, file.filename.replace(" ", "_"))
    with open(file_path, "wb") as f:
        f.write(await file.read())
    output_path = process_sign(file_path)
    if output_path and os.path.exists(output_path):
        return FileResponse(output_path, filename=os.path.basename(output_path))
    cleanup_files()
    raise HTTPException(status_code=500, detail="Failed to sign APK")

@app.post("/process/debug")
async def debug_apk_file(file: UploadFile = File(...)):
    if not file.filename.endswith('.apk'):
        raise HTTPException(status_code=400, detail="File must be an APK")
    file_path = os.path.join(UPLOAD_DIR, file.filename.replace(" ", "_"))
    with open(file_path, "wb") as f:
        f.write(await file.read())
    output_path = debug_apk(file_path, UPLOAD_DIR)
    if output_path and os.path.exists(output_path):
        return FileResponse(output_path, filename=os.path.basename(output_path))
    cleanup_files()
    raise HTTPException(status_code=500, detail="Failed to debug APK")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
