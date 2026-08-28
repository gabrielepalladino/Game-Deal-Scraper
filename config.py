import os
from dotenv import load_dotenv

load_dotenv()

ITAD_API_KEY = os.getenv("ITAD_API_KEY")

if not ITAD_API_KEY:
    raise RuntimeError("ITAD_API_KEY non configurata")
