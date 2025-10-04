from ebay import get_ebay_token
from ebay_post_example import end_item, verify_add_item, get_view_item_url, trading_call
import time
import os
import xml.etree.ElementTree as ET

NS = {"eb": "urn:ebay:apis:eBLBaseComponents"}

def get_ebay_auth_token():
    """Get eBayAuthToken (IAF token) for Trading API from file"""
    token_file = "sandbox_token.txt"
    if os.path.exists(token_file):
        with open(token_file, "r") as f:
            return f.read().strip()
    else:
        raise FileNotFoundError(f"No eBayAuthToken found. Run ebay_post_example.py first to generate {token_file}")

def define_item_details(itemObject: dict | None = None):
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


def add_custom_item(token: str, itemObject: dict | None = None):
    """
    Adds a custom item by taking in a custom XML block.
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
    return item_id_el.text, (ack_el.text if ack_el is not None else "")

def set_listing(itemObject: dict | None, timeBeforeEnd: int = 20): 
    """
    Sets a listing using the provided itemObject dictionary.
    Waits for timeBeforeEnd seconds before ending the listing.
    """
    token = get_ebay_auth_token()
    item_id, ack = add_custom_item(token, itemObject)
    print(f"\nAddItem Ack={ack}, ItemID={item_id}")

    time.sleep(2)

    view_url = get_view_item_url(token, item_id)
    print("ViewItemURL:", view_url or "(not available yet)")

    time.sleep(timeBeforeEnd)
    end_item(token, item_id)
    print(f"\nEnded sandbox listing {item_id}. All done.")
    
    return view_url

if __name__ == "__main__":
    set_listing(None)