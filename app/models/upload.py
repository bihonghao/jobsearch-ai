from __future__ import annotations

from pydantic import BaseModel


class UploadResponse(BaseModel):
    upload_type: str
    file_path: str
    message: str
