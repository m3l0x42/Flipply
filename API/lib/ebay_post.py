# from ebay_post_example import end_item, get_view_item_url, trading_call
import time
import os
import xml.etree.ElementTree as ET
import csv
from datetime import datetime
from pydantic import BaseModel
import requests 

NS = {"eb": "urn:ebay:apis:eBLBaseComponents"}

EBAY_API_URL = "https://api.sandbox.ebay.com/ws/api.dll"

class EbayItemResponse(BaseModel):
    title: str
    description: str
    picture_url: str
    listing_type: str
    listing_duration: str
    start_price: str
    quantity: str
    country: str
    currency: str
    postal_code: str


def upload_picture_to_ebay(token: str, image_data: bytes, image_content_type: str) -> str | None:
    """
    Uploads a picture to eBay Picture Services (EPS) using the Trading API.

    Args:
        token: The eBay Auth Token.
        image_data: The raw binary data of the image.
        image_content_type: The MIME type of the image (e.g., 'image/jpeg').

    Returns:
        The URL of the hosted image on eBay, or None if the upload failed.
    """
    headers = {
        "X-EBAY-API-COMPATIBILITY-LEVEL": "967",
        "X-EBAY-API-DEV-NAME": "YOUR_DEV_NAME",  # Replace with your actual credentials
        "X-EBAY-API-APP-NAME": "YOUR_APP_NAME",  # Replace with your actual credentials
        "X-EBAY-API-CERT-NAME": "YOUR_CERT_NAME", # Replace with your actual credentials
        "X-EBAY-API-CALL-NAME": "UploadSiteHostedPictures",
        "X-EBAY-API-SITEID": "0", # 0 = US
    }

    # The XML part of the multipart request
    xml_payload = f"""<?xml version="1.0" encoding="utf-8"?>
<UploadSiteHostedPicturesRequest xmlns="urn:ebay:apis:eBLBaseComponents">
  <RequesterCredentials>
    <eBayAuthToken>{token}</eBayAuthToken>
  </RequesterCredentials>
  <PictureName>MyListingPhoto</PictureName>
  <ExtensionInDays>30</ExtensionInDays>
</UploadSiteHostedPicturesRequest>"""

    files = {
        'file': ('image', image_data, image_content_type)
    }
    
    # The first part of the multipart data must be the XML
    multipart_data = {
        'XMLPayload': (None, xml_payload, 'application/xml')
    }

    try:
        print("Uploading picture to eBay Picture Services...")
        response = requests.post(EBAY_API_URL, headers=headers, data=multipart_data, files=files)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # Parse the XML response to get the URL
        root = ET.fromstring(response.content)
        ack_el = root.find("eb:Ack", NS)
        ack = ack_el.text if ack_el is not None else "Failure"

        if ack in ["Success", "Warning"]:
            full_url_el = root.find(".//eb:FullURL", NS)
            if full_url_el is not None:
                picture_url = full_url_el.text
                print(f"Picture successfully uploaded to: {picture_url}")
                return picture_url
            else:
                print("Error: Upload successful, but no URL found in response.")
                print(response.text)
                return None
        else:
            print("Error: eBay API returned a failure ACK for image upload.")
            # Find and print errors
            errors = root.findall(".//eb:ShortMessage", NS)
            for error in errors:
                print(f"- {error.text}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"An HTTP error occurred during picture upload: {e}")
        return None
    except ET.ParseError as e:
        print(f"Failed to parse XML response from eBay: {e}")
        return None

def get_ebay_auth_token():
    """Get eBayAuthToken (IAF token) for Trading API from file"""
    token_file = "sandbox_token.txt"
    if os.path.exists(token_file):
        with open(token_file, "r") as f:
            return f.read().strip()
    else:
        raise FileNotFoundError(f"No eBayAuthToken found. Run ebay_post_example.py first to generate {token_file}")

def add_listing_to_csv(item_id: str, title: str = "", csv_file: str = "active_listings.csv"):
    """Add a new listing to the CSV file with timestamp"""
    file_exists = os.path.exists(csv_file)
    
    with open(csv_file, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # Write header if file is new
        if not file_exists:
            writer.writerow(['item_id', 'title', 'created_at'])
        
        # Add the listing
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        writer.writerow([item_id, title, timestamp])
    
    print(f"Added listing {item_id} to {csv_file}")

def remove_listing_from_csv(item_id: str, csv_file: str = "active_listings.csv"):
    """Remove a listing from the CSV file"""
    if not os.path.exists(csv_file):
        print(f"CSV file {csv_file} does not exist")
        return False
    
    # Read all rows except the one to be removed
    rows_to_keep = []
    found = False
    
    with open(csv_file, 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        header = next(reader, None)  # Read header
        if header:
            rows_to_keep.append(header)
        
        for row in reader:
            if len(row) > 0 and row[0] != item_id:  # Keep rows that don't match the item_id
                rows_to_keep.append(row)
            elif len(row) > 0 and row[0] == item_id:
                found = True
    
    # Write back the filtered rows
    with open(csv_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(rows_to_keep)
    
    if found:
        print(f"Removed listing {item_id} from {csv_file}")
    else:
        print(f"Listing {item_id} not found in {csv_file}")
    
    return found

def get_active_listings(csv_file: str = "active_listings.csv"):
    """Get all active listings from the CSV file"""
    if not os.path.exists(csv_file):
        return []
    
    listings = []
    with open(csv_file, 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            listings.append(row)
    
    return listings

def define_item_details(itemObject: EbayItemResponse | None = None):
    """
    Takes in a class or dict of item details and returns the XML block for the item.
    If itemObject is None, uses default values.
    
    Ensure the itemObject contains all necessary fields:

    - title
    - description
    - picture_url
    - listing_type
    - listing_duration
    - start_price
    - quantity
    - country
    - currency
    - postal_code
    """

    if itemObject is None:
        # Default values when no itemObject provided
        title = "Sony WH-1000XM4 Wireless Noise-Cancelling Over-the-Ear Headphones, Black"
        description = "Experience the ultimate in sound quality and comfort with the Sony WH-1000XM4 headphones."
        picture_url = "https://m.media-amazon.com/images/I/61UgZSYRllL._UF894,1000_QL80_.jpg"
        listing_type = "FixedPriceItem"
        listing_duration = "GTC"
        start_price = "299.99"
        quantity = "1"
        country = "US"
        currency = "USD"
        postal_code = "94105"
    else:
        # Use values from itemObject, with fallbacks only if key is missing
        if isinstance(itemObject, dict):
            title = itemObject.get("title", "Default Item Title")
            description = itemObject.get("description", "Default item description")
            picture_url = itemObject.get("picture_url", "https://i.ebayimg.sandbox.ebaystatic.com/aw/pics/s_1x2.gif")
            listing_type = itemObject.get("listing_type", "FixedPriceItem")
            listing_duration = itemObject.get("listing_duration", "GTC")
            start_price = itemObject.get("start_price", "19.99")
            quantity = itemObject.get("quantity", "1")
            country = itemObject.get("country", "US")
            currency = itemObject.get("currency", "USD")
            postal_code = itemObject.get("postal_code", "94105")
        else:
            title = getattr(itemObject, "title", "Default Item Title")
            description = getattr(itemObject, "description", "Default item description")
            picture_url = getattr(itemObject, "picture_url", "https://i.ebayimg.sandbox.ebaystatic.com/aw/pics/s_1x2.gif")
            listing_type = getattr(itemObject, "listing_type", "FixedPriceItem")
            listing_duration = getattr(itemObject, "listing_duration", "GTC")
            start_price = getattr(itemObject, "start_price", "19.99")
            quantity = getattr(itemObject, "quantity", "1")
            country = getattr(itemObject, "country", "US")
            currency = getattr(itemObject, "currency", "USD")
            postal_code = getattr(itemObject, "postal_code", "94105")

    return f"""<Item>
  <Title>{title}</Title>
  <Description>{description}</Description>
  <PictureURL>{picture_url}</PictureURL>

  <PrimaryCategory><CategoryID>9355</CategoryID></PrimaryCategory>
  <ConditionID>1000</ConditionID>

  <ListingType>{listing_type}</ListingType>
  <ListingDuration>{listing_duration}</ListingDuration>        <!-- required for fixed-price -->

  <StartPrice currencyID="{currency}">{start_price}</StartPrice>
  <Quantity>{quantity}</Quantity>

  <Country>{country}</Country>
  <Currency>{currency}</Currency>
  <PostalCode>{postal_code}</PostalCode>
  <DispatchTimeMax>2</DispatchTimeMax>          <!-- handling time -->

  <ItemSpecifics>                                 <!-- required for cat 9355 -->
    <NameValueList><Name>Brand</Name><Value>Apple</Value></NameValueList>
    <NameValueList><Name>Model</Name><Value>iPhone 12</Value></NameValueList>
    <NameValueList><Name>Storage Capacity</Name><Value>128 GB</Value></NameValueList>
    <NameValueList><Name>Color</Name><Value>Black</Value></NameValueList>
  </ItemSpecifics>

  <ReturnPolicy>
    <ReturnsAcceptedOption>ReturnsAccepted</ReturnsAcceptedOption>
    <ReturnsWithinOption>Days_30</ReturnsWithinOption>
    <RefundOption>MoneyBack</RefundOption>
    <ShippingCostPaidByOption>Buyer</ShippingCostPaidByOption>
  </ReturnPolicy>

  <ShippingDetails>
    <ShippingServiceOptions>
      <ShippingServicePriority>1</ShippingServicePriority>
      <ShippingService>USPSPriority</ShippingService>
      <ShippingServiceCost currencyID="USD">5.00</ShippingServiceCost>
    </ShippingServiceOptions>
  </ShippingDetails>

  <PictureDetails>
    <PictureURL>{picture_url}</PictureURL>
  </PictureDetails>

  <CategoryMappingAllowed>true</CategoryMappingAllowed>
</Item>"""


def add_custom_item(token: str, itemObject: EbayItemResponse | None = None):
    """
    Adds a custom item by taking in a custom XML block and records it in CSV.
    """
    item_xml = define_item_details(itemObject)   # <-- Pass itemObject parameter
    xml = f"""<?xml version="1.0" encoding="utf-8"?>
<AddItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">
  <RequesterCredentials><eBayAuthToken>{token}</eBayAuthToken></RequesterCredentials>
  {item_xml}
</AddItemRequest>"""
    resp = trading_call("AddItem", xml)
    root = ET.fromstring(resp)
    item_id_el = root.find("eb:ItemID", NS)
    ack_el = root.find("eb:Ack", NS)
    if item_id_el is None:
        raise RuntimeError(f"AddItem failed:\n{resp}")
    
    item_id = item_id_el.text
    ack = ack_el.text if ack_el is not None else ""
    
    # Add to CSV if successful
    if item_id and ack in ["Success", "Warning"]:
        title = ""
        if itemObject and hasattr(itemObject, 'title'):
            title = itemObject.title
        elif itemObject is None:
            title = "Sony WH-1000XM4 Wireless Noise-Cancelling Over-the-Ear Headphones, Black"
        add_listing_to_csv(item_id, title)
    
    return item_id, ack

def end_item_with_csv_removal(token: str, item_id: str):
    """
    Ends an item listing and removes it from the CSV file.
    """
    result = end_item(token, item_id)
    remove_listing_from_csv(item_id)
    return result

def set_listing(itemObject: EbayItemResponse | None, timeBeforeEnd: int = 20): 
    """
    Sets a listing using the provided itemObject dictionary.
    Waits for timeBeforeEnd seconds before ending the listing.
    """
    token = get_ebay_auth_token()

    # Clean up any existing test listing
    try:
        end_item_with_csv_removal(token, "110588449674")
    except Exception as e:
        print(f"Note: Could not end existing test item: {e}")

    item_id, ack = add_custom_item(token, itemObject)
    print(f"\nAddItem Ack={ack}, ItemID={item_id}")

    if not item_id:
        print("Failed to create listing - no item ID returned")
        return None

    time.sleep(2)

    view_url = get_view_item_url(token, item_id)
    print("ViewItemURL:", view_url or "(not available yet)")

    time.sleep(timeBeforeEnd)
    end_item_with_csv_removal(token, item_id)
    print(f"\nEnded sandbox listing {item_id}. All done.")
    
    return view_url

if __name__ == "__main__":
    set_listing(None)