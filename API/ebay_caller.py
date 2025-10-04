import os
import requests
from dotenv import load_dotenv
import xmltodict


# Load environment variables from .env file
load_dotenv()

SBX_ENDPOINT = "https://api.sandbox.ebay.com/ws/api.dll"

HEADERS = {
    "X-EBAY-API-COMPATIBILITY-LEVEL": "1193",
    "X-EBAY-API-DEV-NAME": os.environ["EBAY_DEV_ID"],
    "X-EBAY-API-APP-NAME": os.environ["EBAY_APP_ID"],
    "X-EBAY-API-CERT-NAME": os.environ["EBAY_CERT_ID"],
    "X-EBAY-API-CALL-NAME": "GetSessionID",
    "X-EBAY-API-SITEID": "0",
    "Content-Type": "text/xml",
}

xml = f"""<?xml version="1.0" encoding="utf-8"?>
<GetSessionIDRequest xmlns="urn:ebay:apis:eBLBaseComponents">
  <RuName>{os.environ["EBAY_RUNAME"]}</RuName>
</GetSessionIDRequest>
"""

resp = requests.post(SBX_ENDPOINT, data=xml.encode("utf-8"), headers=HEADERS)
parsed = xmltodict.parse(resp.text)
session_id = parsed["GetSessionIDResponse"]["SessionID"] ## to be used for user authentication

auth_url = f"https://signin.sandbox.ebay.com/ws/eBayISAPI.dll?SignIn&runame={os.environ['EBAY_RUNAME']}&SessID={session_id}"

print(auth_url)  # URL for user authentication