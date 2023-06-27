from typing import Optional
from dataclasses import dataclass


@dataclass
class HTTPResponse:
    status_code: int
    content_type: Optional[str]
    body: bytes
