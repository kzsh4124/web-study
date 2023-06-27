from typing import Optional, Union
from dataclasses import dataclass


@dataclass
class HTTPResponse:


    body: Union[bytes, str]
    content_type: Optional[str] = None
    status_code: int = 200
