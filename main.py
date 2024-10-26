from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import cv2
import numpy as np
from io import BytesIO
from PIL import Image
import base64
import wave
from fastapi import Request

app = FastAPI()

# Serve static files (JavaScript and CSS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve HTML templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Endpoint 1: Image Upload and Contours Detection
@app.post("/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    # Read image from the uploaded file
    image_bytes = await file.read()
    np_array = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

    # Convert to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply edge detection
    edges = cv2.Canny(gray_image, 100, 200)

    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Draw contours on the original image
    result_image = image.copy()
    cv2.drawContours(result_image, contours, -1, (0, 255, 0), 2)

    # Convert the result back to an image format
    pil_image = Image.fromarray(cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB))
    buffer = BytesIO()
    pil_image.save(buffer, format="JPEG")
    buffer.seek(0)

    return StreamingResponse(buffer, media_type="image/jpeg")

# Endpoint 2: Text to Base64 Encoding
class TextData(BaseModel):
    text: str

@app.post("/encode-base64/")
async def encode_base64(data: TextData):
    # Encode the input text to Base64
    encoded_bytes = base64.b64encode(data.text.encode('utf-8'))
    encoded_str = encoded_bytes.decode('utf-8')
    
    return {"original_text": data.text, "base64_encoded_text": encoded_str}

# Endpoint 3: Audio Fast-Forward (WAV files only)
@app.post("/fast-forward-audio/")
async def fast_forward_audio(file: UploadFile = File(...), fast_forward_time: int = 5000):
    # Ensure the file is in WAV format
    if file.filename.split(".")[-1].lower() != "wav":
        return {"error": "Only WAV files are supported."}

    # Open the WAV file using the wave module
    with wave.open(file.file, 'rb') as wav_file:
        params = wav_file.getparams()
        frame_rate = params.framerate
        num_channels = params.nchannels
        sampwidth = params.sampwidth

        # Calculate the number of frames to skip (fast-forward)
        fast_forward_frames = int((fast_forward_time / 1000) * frame_rate)
        
        # Read frames after the fast-forward point
        wav_file.setpos(min(fast_forward_frames, wav_file.getnframes()))
        audio_frames = wav_file.readframes(wav_file.getnframes() - fast_forward_frames)

    # Write the fast-forwarded audio into a new WAV file in memory
    buffer = BytesIO()
    with wave.open(buffer, 'wb') as output_wav:
        output_wav.setnchannels(num_channels)
        output_wav.setsampwidth(sampwidth)
        output_wav.setframerate(frame_rate)
        output_wav.writeframes(audio_frames)
    
    buffer.seek(0)
    
    return StreamingResponse(buffer, media_type="audio/wav")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
