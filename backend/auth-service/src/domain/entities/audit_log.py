from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class AuditLog:
    id: Optional[int]
    user_id: int
    module: str
    action: str
    timestamp: datetime
    ip_address: str