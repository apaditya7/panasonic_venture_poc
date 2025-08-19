from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime
from enum import Enum

class MachineType(str, Enum):
    INJECTION_MOLDING = "injection_molding"
    CNC_MILL = "cnc_mill"
    CONVEYOR = "conveyor"

class MachineStatus(str, Enum):
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    OFFLINE = "offline"

class Range(BaseModel):
    min: float
    max: float

class NormalRanges(BaseModel):
    temperature: Range
    pressure: Range
    vibration: Range
    rpm: Range
    power_consumption: Range

class Machine(BaseModel):
    id: str
    name: str
    type: MachineType
    normal_ranges: NormalRanges

class MachineData(BaseModel):
    machine_id: str
    timestamp: datetime
    temperature: float
    pressure: float
    vibration: float
    rpm: float
    power_consumption: float
    status: MachineStatus
    anomaly_score: Optional[float] = None
    
class MachineDataResponse(BaseModel):
    machine_id: str
    name: str
    type: str
    status: MachineStatus
    data: Dict[str, float]
    anomaly_score: Optional[float] = None
    last_updated: datetime