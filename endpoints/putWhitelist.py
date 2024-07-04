from typing import List
from settings import settings
from pydantic import BaseModel

class PutWhiteList(BaseModel):
   apiKeys: List[str]

def update_whitelist(whitelist: PutWhiteList):
   settings.apikey_whitelist=whitelist.apiKeys