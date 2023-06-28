from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field

@dataclass
class Cookie:
    name: str
    value: str
    expires: Optional[datetime] = None
    max_age: Optional[int] = None
    domain: str = ""
    path: str = ""
    secure: bool = False
    http_only: bool = False
