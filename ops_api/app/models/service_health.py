"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""Service health model."""
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ServiceHealth:
    id: int
    service_name: str
    status: str
    last_check: datetime
    response_time_ms: float
