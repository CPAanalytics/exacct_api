from pydantic import BaseModel

class User(BaseModel):
    id: str
    is_superuser: bool
    email: str
    tenant_id: str