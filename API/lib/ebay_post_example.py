import os, time, urllib.parse, xml.etree.ElementTree as ET
import requests
from dotenv import load_dotenv

load_dotenv()

SBX_ENDPOINT = "https://api.sandbox.ebay.com/ws/api.dll"
NS = {"eb": "urn:ebay:apis:eBLBaseComponents"}

BASE_HEADERS = {
    "X-EBAY-API-COMPATIBILITY-LEVEL": "1193",
    "X-EBAY-API-DEV-NAME": "57016d2d-f4a4-424d-98c5-81f93508e0f3",
    "X-EBAY-API-APP-NAME": "JuanFern-HackHarv-SBX-788fbab9a-6f33a2ab",
    "X-EBAY-API-CERT-NAME": "SBX-88fbab9a6687-6f93-4d5e-a5df-db99",
    "X-EBAY-API-SITEID": "0",
    "Content-Type": "text/xml",
}

def build_item_xml():
    return """<Item>
  <Title>Sandbox Test Item</Title>
  <Description>Test listing (Sandbox only)</Description>

  <PrimaryCategory><CategoryID>9355</CategoryID></PrimaryCategory>
  <ConditionID>1000</ConditionID>

  <ListingType>FixedPriceItem</ListingType>
  <ListingDuration>GTC</ListingDuration>        <!-- required for fixed-price -->

  <StartPrice currencyID="USD">19.99</StartPrice>
  <Quantity>1</Quantity>

  <Country>US</Country>
  <Currency>USD</Currency>
  <PostalCode>94105</PostalCode>
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
    <PictureURL>https://i.ebayimg.sandbox.ebaystatic.com/aw/pics/s_1x2.gif</PictureURL>
  </PictureDetails>

  <CategoryMappingAllowed>true</CategoryMappingAllowed>
</Item>"""

def trading_call(call_name: str, xml_body: str) -> str:
    headers = dict(BASE_HEADERS)
    headers["X-EBAY-API-CALL-NAME"] = call_name
    r = requests.post(SBX_ENDPOINT, data=xml_body.encode("utf-8"), headers=headers, timeout=60)
    r.raise_for_status()
    return r.text

def get_session_id(runame: str) -> str:
    xml = f'''<?xml version="1.0" encoding="utf-8"?>
<GetSessionIDRequest xmlns="urn:ebay:apis:eBLBaseComponents">
  <RuName>{runame}</RuName>
</GetSessionIDRequest>'''
    resp = trading_call("GetSessionID", xml)
    root = ET.fromstring(resp)
    sid = root.find("eb:SessionID", NS)
    if sid is None:
        raise RuntimeError(f"GetSessionID failed:\n{resp}")
    return sid.text

def fetch_token(session_id: str) -> tuple[str, str]:
    xml = f'''<?xml version="1.0" encoding="utf-8"?>
<FetchTokenRequest xmlns="urn:ebay:apis:eBLBaseComponents">
  <SessionID>{session_id}</SessionID>
</FetchTokenRequest>'''
    resp = trading_call("FetchToken", xml)
    root = ET.fromstring(resp)
    token = root.find("eb:eBayAuthToken", NS)
    expiry = root.find("eb:HardExpirationTime", NS)
    if token is None:
        raise RuntimeError(f"FetchToken failed:\n{resp}")
    return token.text, (expiry.text if expiry is not None else "")

def verify_add_item(token: str):
    item_xml = build_item_xml()
    xml = f"""<?xml version="1.0" encoding="utf-8"?>
<VerifyAddItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">
  <RequesterCredentials><eBayAuthToken>{token}</eBayAuthToken></RequesterCredentials>
  {item_xml}
</VerifyAddItemRequest>"""
    resp = trading_call("VerifyAddItem", xml)
    root = ET.fromstring(resp)
    ack = (root.find("eb:Ack", NS).text if root.find("eb:Ack", NS) is not None else "Failure")
    return (ack in ("Success", "Warning")), resp

def add_item(token: str):
    item_xml = build_item_xml()   # <-- SAME BLOCK
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


def add_xm4(token: str):
    item_xml = build_xm4_listing()  # <-- SAME BLOCK
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

def end_item(token: str, item_id: str) -> None:
    xml = f'''<?xml version="1.0" encoding="utf-8"?>
<EndItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">
  <RequesterCredentials><eBayAuthToken>{token}</eBayAuthToken></RequesterCredentials>
  <ItemID>{item_id}</ItemID>
  <EndingReason>NotAvailable</EndingReason>
</EndItemRequest>'''
    _ = trading_call("EndItem", xml)


NS = {"eb": "urn:ebay:apis:eBLBaseComponents"}

def get_view_item_url(token: str, item_id: str, retries: int = 5, delay_sec: float = 1.0) -> str | None:
    """Fetch the canonical ViewItemURL for a newly created listing.
       Retries briefly in case the URL isn’t populated immediately."""
    req = f'''<?xml version="1.0" encoding="utf-8"?>
<GetItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">
  <RequesterCredentials><eBayAuthToken>{token}</eBayAuthToken></RequesterCredentials>
  <ItemID>{item_id}</ItemID>
  <DetailLevel>ReturnAll</DetailLevel>
</GetItemRequest>'''
    for _ in range(retries):
        resp_xml = trading_call("GetItem", req)
        root = ET.fromstring(resp_xml)
        url_el = root.find(".//eb:ViewItemURL", NS)
        status_el = root.find(".//eb:ListingStatus", NS)
        if url_el is not None and url_el.text:
            return url_el.text
        # tiny backoff in case Sandbox needs a moment
        time.sleep(delay_sec)
    return None

if __name__ == "__main__":
    runame = os.environ["EBAY_RUNAME"]
    # 1) Get SessionID
    session_id = get_session_id(runame)
    signin = (
        "https://signin.sandbox.ebay.com/ws/eBayISAPI.dll"
        f"?SignIn&RuName={urllib.parse.quote(runame)}"
        f"&SessID={urllib.parse.quote(session_id)}"
    )
    print("\nOpen this URL, log in as your SANDBOX seller, and approve access:\n")
    print(signin)
    input("\nAfter approving, press ENTER to continue... ")

    # 2) Exchange SessionID -> eBayAuthToken
    token, expiry = fetch_token(session_id)
    print("\nGot eBayAuthToken (sandbox). Expires:", expiry or "(n/a)")
    # Persist simply for dev (use encrypted storage in real apps)
    with open("sandbox_token.txt", "w") as f:
        f.write(token)

    # # 3) Verify, then Add
    # ok, verify_resp = verify_add_item(token)
    # print("\nVerifyAddItem:", "OK" if ok else "FAILED")
    # if not ok:
    #     # Print response to debug missing fields (e.g., ShippingDetails/ReturnPolicy)
    #     print(verify_resp)
    #     raise SystemExit(1)

    item_id, ack = add_item(token)
    print(f"\nAddItem Ack={ack}, ItemID={item_id}")


    time.sleep(2)

    view_url = get_view_item_url(token, item_id)
    print("ViewItemURL:", view_url or "(not available yet)")

    # # 4) Clean up so sandbox stays tidy
    # time.sleep(2)
    # end_item(token, item_id)
    # print(f"\nEnded sandbox listing {item_id}. All done.")


def build_xm4_listing():

    title = "Sony WH-1000XM4 Wireless Noise-Cancelling Over-the-Ear Headphones, Black"
    description = "Experience the ultimate in sound quality and comfort with the Sony WH-1000XM4 headphones."
    picture_url = "https://m.media-amazon.com/images/I/61UgZSYRllL._UF894,1000_QL80_.jpg"

    return f"""<Item>
  <Title>{title}</Title>
  <Description>{description}</Description>
  <PictureURL>{picture_url}</PictureURL>

  <PrimaryCategory><CategoryID>9355</CategoryID></PrimaryCategory>
  <ConditionID>1000</ConditionID>

  <ListingType>FixedPriceItem</ListingType>
  <ListingDuration>GTC</ListingDuration>        <!-- required for fixed-price -->

  <StartPrice currencyID="USD">19.99</StartPrice>
  <Quantity>1</Quantity>

  <Country>US</Country>
  <Currency>USD</Currency>
  <PostalCode>94105</PostalCode>
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