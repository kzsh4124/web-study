from dataclasses import dataclass, field


@dataclass
class HTTPRequest:
    path: str
    method: str
    http_version: str
    body: bytes
    headers: dict = field(default_factory=dict)
