"""Alert model."""
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Alert:
    id: int
    severity: str
    message: str
    source: str
    created_at: datetime
    resolved: bool = False
