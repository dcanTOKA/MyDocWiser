from pydantic import BaseModel
from typing import List, Optional


class Document(BaseModel):
    title: str
    content: str
    sub_documents: Optional[List['Document']] = None


Document.update_forward_refs()
