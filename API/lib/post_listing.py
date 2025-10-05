import os
import datetime
from ebaysdk.exception import ConnectionError
from ebaysdk.trading import Connection as Trading

def upload_image_to_ebay(api, image_path):
    """
    Uploads an image to eBay Picture Services (EPS) and returns the URL.
    """
    try:
        files = {'file': ('image', open(image_path, 'rb'))}
        picture_details = {
            'PictureName': "MyListingImage" 
        }
        
        print("Uploading image to eBay...")
        response = api.execute('UploadSiteHostedPictures', picture_details, files=files)
        
        if response.reply.Ack == 'Success':
            image_url = response.reply.SiteHostedPictureDetails.FullURL
            print(f"Image uploaded successfully. URL: {image_url}")
            return image_url
        else:
            print("Error uploading image:")
            for error in response.reply.Errors:
                print(f"- {error.ShortMessage}: {error.LongMessage}")
            return None

    except ConnectionError as e:
        print(f"Connection Error during image upload: {e}")
        print(e.response.dict())
        return None

def create_listing(api, image_url, title, descr, price, condition):
    """
    Creates a new fixed-price listing on eBay.
    """
    try:
        category_id = '261186'

        item_details = {
            "Item": {
                "Title": title,
                "Description": descr,
                "PrimaryCategory": {"CategoryID": category_id},
                "StartPrice": price,
                "ConditionID": "1000" if condition == "excellent" else 3000,
                "Country": "US",
                "Currency": "USD",
                "DispatchTimeMax": "3",
                "ListingDuration": "GTC",
                "ListingType": "FixedPriceItem",
                "PictureDetails": {
                    "PictureURL": image_url
                },
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
                        {'Name': 'Book Title', 'Value': title}, # Best practice to match the item title
                        {'Name': 'Author', 'Value': 'A. Cheesemaker'}, # Example value
                        {'Name': 'Language', 'Value': 'English'} # Example value
                    ]
                }
            }
        }
        
        print("\nCreating the listing with final completed data...")
        response = api.execute('AddItem', item_details)
        
        if response.reply.Ack == 'Success':
            item_id = response.reply.ItemID
            print("==========================================")
            print("      LISTING CREATED SUCCESSFULLY!       ")
            print("==========================================")
            print(f"ItemID: {item_id}")
            print(f"View your sandbox listing at: https://sandbox.ebay.com/itm/{item_id}")
        else:
            print("Error creating listing:")
            for error in response.reply.Errors:
                if error.SeverityCode == 'Error':
                    print(f"- {error.ShortMessage}: {error.LongMessage}")

    except ConnectionError as e:
        print(f"Connection Error during listing creation: {e}")
        print(e.response.dict())

if __name__ == "__main__":
    # --- HARDCODE CREDENTIALS FOR DEBUGGING ---
    # Paste your credentials from your ebay.yaml file directly here.
    # Ensure they are strings (inside quotes).

    MY_SANDBOX_APP_ID = "JuanFern-HackHarv-SBX-788fbab9a-6f33a2ab"
    MY_SANDBOX_DEV_ID = "57016d2d-f4a4-424d-98c5-81f93508e0f3"
    MY_SANDBOX_CERT_ID = "SBX-88fbab9a6687-6f93-4d5e-a5df-db99"
    MY_SANDBOX_TOKEN = "v^1.1#i^1#f^0#r^1#I^3#p^3#t^Ul4xMF8yOjgzNjQ1NkYxMzExNjA4NEZEQUMyQTc5OTQyREMwNzlGXzFfMSNFXjEyODQ="
    
    # ---------------------------------------------

    # Ensure you have a test image named 'test.jpg' in the same directory
    image_file_path = "test.jpg"
    if not os.path.exists(image_file_path):
        print(f"Error: Image file not found at '{image_file_path}'")
        print("Please create a dummy image file with that name to run this script.")
    else:
        try:
            print("Initializing API connection with hardcoded credentials...")
            
            # Initialize the Trading API, passing credentials directly
            # instead of using config_file
            api = Trading(
                domain='api.sandbox.ebay.com', # CRITICAL: This targets the sandbox
                appid=MY_SANDBOX_APP_ID,
                devid=MY_SANDBOX_DEV_ID,
                certid=MY_SANDBOX_CERT_ID,
                token=MY_SANDBOX_TOKEN,
                config_file=None # Explicitly disable config file loading
            )
            
            # Step 1: Upload the image
            hosted_image_url = upload_image_to_ebay(api, image_file_path)
            
            # Step 2: If image upload was successful, create the listing
            if hosted_image_url:
                # api, image_url, title, descr, price, condition
                create_listing(api, hosted_image_url, "cheese", "some cheese", 20, "good")

        except ConnectionError as e:
            # This is a more specific catch for API connection issues
            print(f"A ConnectionError occurred: {e}")
            print("Full response details:")
            print(e.response.text) # Print the raw text from eBay's server
        except Exception as e:
            print(f"An unexpected error occurred: {e}")