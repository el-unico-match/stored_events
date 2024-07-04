from datetime import datetime
from pydantic import BaseModel


class EventIn(BaseModel):
   action: str
   state: str
   data: str
   processid: str

class UserEventIn(BaseModel):
   userid: str
   action: str
   state: str
   data: str
   processid: str

class UserParams(BaseModel):
   userid: str

class FederatedUserParams(UserParams):
   federated_identity: str
   email: str

class HttpResult(UserParams):
   status_code: str
   delay_ms: int

class BlockedUserParams(UserParams):
   reason: str

class UserAction(UserParams):
   action: str
      # like
      # rewind
      # send_message
   
class ResetPasswordParams(BaseModel):
   email: str
   token: str