import os
import io
from ebaysdk.exception import ConnectionError
from ebaysdk.trading import Connection as Trading
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Pydantic Model for the Response ---
class EbayItemResponse(BaseModel):
    itemId: str
    listingUrl: str
    status: str

# --- MODIFIED: Accepts image_bytes instead of a path ---
def _upload_image_to_ebay(api, image_bytes: bytes):
    """
    Uploads an image from bytes to eBay Picture Services (EPS).
    """
    # The ebaysdk expects a file-like object, so we wrap the bytes in io.BytesIO
    files = {'file': ('image.jpg', io.BytesIO(image_bytes))}
    picture_details = {'PictureName': "ListingImage"}
    
    print("Uploading image to eBay...")
    response = api.execute('UploadSiteHostedPictures', picture_details, files=files)
    
    if response.reply.Ack == 'Success':
        image_url = response.reply.SiteHostedPictureDetails.FullURL
        print(f"Image uploaded successfully. URL: {image_url}")
        return image_url
    else:
        # Raise an exception to be caught by the API endpoint
        errors = [e.LongMessage for e in response.reply.Errors]
        raise Exception(f"Error uploading image to eBay: {', '.join(errors)}")

def _create_listing(api, image_url, title, descr, price, condition, author, language):
    """
    Creates the eBay listing.
    """
    category_id = '261186' # Books > Antiquarian & Collectible

    item_details = {
        "Item": {
            "Title": title,
            "Description": descr,
            "PrimaryCategory": {"CategoryID": category_id},
            "StartPrice": str(price),
            "ConditionID": "1000" if condition.lower() in ["new", "excellent", "like new"] else "3000",
            "Country": "US",
            "Currency": "USD",
            "DispatchTimeMax": "3",
            "ListingDuration": "GTC",
            "ListingType": "FixedPriceItem",
            "PictureDetails": {"PictureURL": image_url},
            "PostalCode": "95125",
            "Quantity": "1",
            "ReturnPolicy": {
                "ReturnsAcceptedOption": "ReturnsAccepted",
                "RefundOption": "MoneyBack",
                "ReturnsWithinOption": "Days_30",
                "ShippingCostPaidByOption": "Buyer"
            },
            "ShippingDetails": {
                "ShippingType": "Flat",
                "ShippingServiceOptions": {
                    "ShippingServicePriority": "1",
                    "ShippingService": "USPSMedia",
                    "ShippingServiceCost": "2.50"
                }
            },
            "Site": "US",
            "ItemSpecifics": {
                "NameValueList": [
                    {'Name': 'Book Title', 'Value': title},
                    {'Name': 'Author', 'Value': author},
                    {'Name': 'Language', 'Value': language}
                ]
            }
        }
    }
    
    print("\nCreating the listing...")
    response = api.execute('AddItem', item_details)
    
    if response.reply.Ack == 'Success':
        item_id = response.reply.ItemID
        print(f"Listing created successfully! ItemID: {item_id}")
        return item_id
    else:
        errors = [e.LongMessage for e in response.reply.Errors]
        raise Exception(f"Error creating eBay listing: {', '.join(errors)}")

# --- Main function to be called from FastAPI ---
def create_ebay_listing(title: str, description: str, price: float, condition: str, image_data: bytes):
    """
    Orchestrates the full process of creating an eBay listing.
    """
    try:
        # Initialize the Trading API using credentials from environment variables
        api = Trading(
            domain='api.sandbox.ebay.com',
            appid=os.environ.get("EBAY_SANDBOX_APP_ID"),
            devid=os.environ.get("EBAY_SANDBOX_DEV_ID"),
            certid=os.environ.get("EBAY_SANDBOX_CERT_ID"),
            token=os.environ.get("EBAY_SANDBOX_TOKEN"),
            config_file=None
        )
        
        # Step 1: Upload the image
        hosted_image_url = _upload_image_to_ebay(api, image_data)
        
        # Step 2: Create the listing
        # For simplicity, hardcoding author/language, but you could pass these in too
        item_id = _create_listing(
            api, hosted_image_url, title, description, price, condition, 
            author="Various", language="English"
        )
        
        # Step 3: Return a structured response
        return EbayItemResponse(
            itemId=item_id,
            listingUrl=f"https://sandbox.ebay.com/itm/{item_id}",
            status="Success"
        )

    except ConnectionError as e:
        print(f"eBay Connection Error: {e}")
        # Re-raise with a more user-friendly message
        raise Exception(f"Could not connect to eBay API: {e.response.reason}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        # Re-raise the exception to be handled by the FastAPI endpoint
        raise e