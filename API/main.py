import vertexai
from vertexai.generative_models import GenerativeModel, Part, Image, GenerationConfig
from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel, Field
import uvicorn
import json
import os
from typing import List
from lib.ebay import search_items

PROJECT_ID = os.environ["PROJECT_ID"]
MAX_RETRIES = 3

try:
    vertexai.init(project=PROJECT_ID)
    model = GenerativeModel("gemini-2.5-flash")
except Exception as e:
    print(
        f"Fatal: Could not initialize Vertex AI. Please check your authentication. Error: {e}")

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
    imageQuality: str = Field(...)

@app.post("/analyze-image/", response_model=ImageAnalysisResponse)
async def analyze_image(image: UploadFile = File(...)):
    if not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400, detail="Invalid file type. Please upload an image.")
    try:
        image_data = await image.read()
        image_part = Part.from_data(
            data=image_data, mime_type=image.content_type)
    except Exception as e:
        print(f"Error reading file: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to read uploaded image: {e}")

    generation_config = GenerationConfig(
        response_mime_type="application/json",
    )

    prompt_1_identify = """
    You are an expert e-commerce analyst. Your task is to identify the item in the image and provide structured data about it.
    The primary goal is to extract accurate keywords for a second-pass market analysis.
    You MUST respond with ONLY a valid JSON object. Do not include any other text, explanations, or markdown formatting like ```json.

    Use the following JSON schema:
    {
      "item": "The most likely name of the item.",
      "brand": "The brand of the item, or 'Unknown' if not identifiable.",
      "description": "A concise, one-sentence description of the item.",
      "imageQuality": "An classification of the image quality (Excellent, Good, Fair, Poor).",
      "searchKeywords": [
        "A list of 3-5 precise string keywords for finding this item on a marketplace like eBay."
      ],
      "condition": "Item condition based on visual inspection (e.g., 'New', 'Used - Like New', 'Used - Good', 'For parts')."
    }
    """

    initial_analysis_json = None
    for attempt in range(MAX_RETRIES):
        try:
            response = await model.generate_content_async(
                [image_part, prompt_1_identify],
                stream=False,
                generation_config=generation_config
            )
            initial_analysis_json = json.loads(response.text)
            break
        except Exception as e:
            print(f"An error occurred during identification (attempt {attempt + 1}): {e}")
            if attempt == MAX_RETRIES - 1:
                 raise HTTPException(
                    status_code=503,
                    detail=f"The model failed to identify the item after {MAX_RETRIES} attempts."
                )

    search_query = " ".join(initial_analysis_json.get("searchKeywords", []))
    if not search_query:
        raise HTTPException(status_code=400, detail="Could not generate search keywords from image.")

    try:
        ebay_listings = await search_items(search_query, limit=10)
        print(f"Ebay listigs found: {ebay_listings}")
    except Exception as e:
        print(f"Error searching eBay: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch listings from eBay: {e}")

    prompt_2_price = f"""
    You are an expert e-commerce price analyst. Your task is to provide a price estimate for the item shown in the image,
    based on its description and a list of comparable items found on eBay.

    Analyze the provided item information, the image itself (paying attention to condition), and the market data.
    Consider how the item's condition compares to the listings. Provide a realistic price range and a suggested price. Ignore irrelevant listings.

    You MUST respond with ONLY a valid JSON object. Do not include any other text, explanations, or markdown formatting.

    **Item to be Priced:**
    ```json
    {json.dumps(initial_analysis_json, indent=2)}
    ```

    **Comparable eBay Listings (Market Data):**
    ```json
    {json.dumps(ebay_listings, indent=2)}
    ```

    **Required Output JSON Schema:**
    {{
      "estimatedPrice": {{
        "min": Minimum price,
        "max": Maximum item price,
        "suggested": Suggested item price,
      }}
    }}
    """

    print(prompt_2_price)

    price_analysis_json = None
    for attempt in range(MAX_RETRIES):
        try:
            # We include the image again so the model can visually compare its condition
            # against the descriptions and prices in the eBay listings.
            response = await model.generate_content_async(
                [image_part, prompt_2_price],
                stream=False,
                generation_config=generation_config
            )
            price_analysis_json = json.loads(response.text)
            break # Success, exit loop
        except Exception as e:
            print(f"An error occurred during pricing (attempt {attempt + 1}): {e}")
            if attempt == MAX_RETRIES - 1:
                raise HTTPException(
                    status_code=503,
                    detail=f"The model failed to price the item after {MAX_RETRIES} attempts."
                )

    # --- MODIFICATION 5: Combine results and return ---
    # Merge the results from the identification step and the pricing step.
    final_response = initial_analysis_json
    final_response["estimatedPrice"] = price_analysis_json.get(
        "estimatedPrice", {"min": 0.0, "max": 0.0, "suggested": 0.0}
    )

    return final_response


@app.get("/")
async def read_root():
    return {"message": "Hello world!"}


if __name__ == "__main__":
    # It's good practice to ensure the port is an integer
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)