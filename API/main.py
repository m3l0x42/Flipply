import vertexai
from vertexai.generative_models import GenerativeModel, Part, Image, GenerationConfig
from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel, Field
import uvicorn
import json
import os
from typing import List

PROJECT_ID = os.environ["PROJECT_ID"]
MAX_RETRIES = 3

try:
    vertexai.init(project=PROJECT_ID)
    model = GenerativeModel("gemini-2.5-flash")
except Exception as e:
    print(f"Fatal: Could not initialize Vertex AI. Please check your authentication. Error: {e}")

app = FastAPI(
    title="HackHarvard API",
)

class EstimatedPrice(BaseModel):
    min: float = Field(...)
    max: float = Field(...)
    suggested: float = Field(...)

class ImageAnalysisResponse(BaseModel):
    item: str = Field(...)
    brand: str = Field(...)
    description: str = Field(...)
    searchKeywords: List[str] = Field(...)
    condition: str = Field(...)
    estimatedPrice: EstimatedPrice

@app.post("/analyze-image/", response_model=ImageAnalysisResponse)
def analyze_image(image: UploadFile = File(...)):
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")
    try:
        image_data = image.file.read()
        
        image_part = Part.from_data(data=image_data, mime_type=image.content_type)

    except Exception as e:
        print(f"Error reading file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to read uploaded image: {e}")
    
    prompt = """
    You are an expert e-commerce analyst. Your task is to identify the item in the image and provide structured data about it.
    You MUST respond with ONLY a valid JSON object. Do not include any other text, explanations, or markdown formatting like ```json.

    Use the following JSON schema:
    {
      "item": "The most likely name of the item.",
      "brand": "The brand of the item, or 'Unknown' if not identifiable.",
      "description": "A concise, one-sentence description of the item.",
      "searchKeywords": [
        "A list of 3-5 precise string keywords for finding this item online."
      ],
      "condition": "Item condition (e.g., 'New', 'Used - Like New', 'Used - Good', 'For parts').",
      "estimatedPrice": {
        "min": 0.0,
        "max": 0.0,
        "suggested": 0.0
      }
    }
    """
    
    generation_config = GenerationConfig(
        response_mime_type="application/json",
    )

    for attempt in range(MAX_RETRIES):
        try:
            response = model.generate_content(
                [image_part, prompt], 
                stream=False,
                generation_config=generation_config
            )
            return json.loads(response.text)

        except Exception as e:
            print(f"An error occurred on attempt {attempt + 1}: {e}")

    raise HTTPException(
        status_code=503, 
        detail=f"The model failed to provide a valid response after {MAX_RETRIES} attempts."
    )

@app.get("/")
def read_root():
    return {"message": "Hello world!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)