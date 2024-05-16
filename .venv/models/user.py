# /app/models/user.py

from uuid import UUID
from pydantic import BaseModel, ConfigDict

class Deliveryman(BaseModel):
 model_config = ConfigDict(from_attributes=True)

 id: UUID
 name: str
 passwd: str