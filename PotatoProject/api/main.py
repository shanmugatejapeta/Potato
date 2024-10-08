from fastapi import FastAPI, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import numpy as np
from io import BytesIO
from PIL import Image
import tensorflow as tf
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("templates/index.html", "r") as file:
        content = file.read()
    return HTMLResponse(content=content)

MODEL = tf.keras.models.load_model("potatoes.keras")

CLASS_NAMES = ["Early Blight", "Late Blight", "Healthy"]

templates = Jinja2Templates(directory="templates")

def read_file_as_image(data) -> np.ndarray:
    image = np.array(Image.open(BytesIO(data)))
    return image

@app.post("/predict")
async def predict(
    request: Request,
    file: UploadFile = File(...)
):
    image = read_file_as_image(await file.read())
    img_batch = np.expand_dims(image, 0)
    
    predictions = MODEL.predict(img_batch)

    predicted_class = CLASS_NAMES[np.argmax(predictions[0])]
    confidence = np.max(predictions[0])

    result_text = f"Predicted Class: {predicted_class}"
    confidence_text=f"Confidence: {confidence}"
    return templates.TemplateResponse("result.html", {"request": request, "result_text": result_text, "confidence_text": confidence_text})

if __name__ == "__main__":
    uvicorn.run(app, host='localhost', port=8000)

