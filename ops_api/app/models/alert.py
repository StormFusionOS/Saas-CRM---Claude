"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

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
