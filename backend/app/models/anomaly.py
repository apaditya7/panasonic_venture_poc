from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AnomalyAlert(BaseModel):
    id: str
    machine_id: str
    severity: str  # "low", "medium", "high"
    message: str
    metric: str  # which metric triggered the anomaly
    value: float
    expected_range: str
    timestamp: datetime
    resolved: bool = False
    ai_analysis: Optional[str] = None