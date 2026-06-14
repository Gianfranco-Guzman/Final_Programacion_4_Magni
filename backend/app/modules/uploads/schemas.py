from pydantic import BaseModel, Field


class CloudinaryResponse(BaseModel):
    secure_url: str = Field(...)
    public_id: str = Field(...)
    width: int = Field(...)
    height: int = Field(...)
    format: str = Field(...)
    resource_type: str = Field(...)
