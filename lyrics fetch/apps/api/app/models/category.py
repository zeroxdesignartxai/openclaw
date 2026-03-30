from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class CategorySchema(BaseModel):
    id: UUID
    slug: str
    name: str
    pipeline_enabled: bool
    public_output_template: Optional[str] = None

    class Config:
        orm_mode = True
