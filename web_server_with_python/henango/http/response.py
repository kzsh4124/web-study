from typing import Optional, Union, List
from dataclasses import dataclass, field
from henango.http.cookie import Cookie

@dataclass
class HTTPResponse:


    body: Union[bytes, str] =b""
    content_type: Optional[str] = None
    status_code: int = 200
    headers: dict = field(default_factory=dict)
    cookies: List[Cookie] = field(default_factory=list)
