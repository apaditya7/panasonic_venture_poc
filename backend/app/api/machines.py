from fastapi import APIRouter, HTTPException
from typing import List
from models.machine import Machine, MachineDataResponse
from services.machine_service import MachineService
from services.data_generator import DataGenerator
from services.anomaly_detector import AnomalyDetector

router = APIRouter()

machine_service = MachineService()
data_generator = DataGenerator()
anomaly_detector = AnomalyDetector()

@router.get("/machines", response_model=List[Machine])
async def get_all_machines():
    return machine_service.get_all_machines()

@router.get("/machines/{machine_id}", response_model=Machine)
async def get_machine(machine_id: str):
    machine = machine_service.get_machine(machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    return machine

@router.get("/machines/data/current", response_model=List[MachineDataResponse])
async def get_current_machine_data():
    for machine in machine_service.get_all_machines():
        data = data_generator.generate_realistic_data(machine)
        anomaly_score = anomaly_detector.calculate_anomaly_score(machine, data)
        data.anomaly_score = anomaly_score
        machine_service.update_machine_data(machine.id, data)
    return machine_service.get_all_machine_data()

@router.get("/machines/{machine_id}/data", response_model=MachineDataResponse)
async def get_machine_data(machine_id: str):
    """Get current data for a specific machine"""
    machine = machine_service.get_machine(machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    # Generate fresh data
    data = data_generator.generate_realistic_data(machine)
    
    # Calculate anomaly score
    anomaly_score = anomaly_detector.calculate_anomaly_score(machine, data)
    data.anomaly_score = anomaly_score
    
    # Update machine data
    machine_service.update_machine_data(machine_id, data)
    
    # Return formatted response
    return MachineDataResponse(
        machine_id=machine_id,
        name=machine.name,
        type=machine.type.value,
        status=data.status,
        data={
            "temperature": data.temperature,
            "pressure": data.pressure,
            "vibration": data.vibration,
            "rpm": data.rpm,
            "power_consumption": data.power_consumption
        },
        anomaly_score=data.anomaly_score,
        last_updated=data.timestamp
    )

@router.post("/machines/{machine_id}/analyze")
async def analyze_machine_anomaly(machine_id: str):
    """Analyze current machine data for anomalies using AI"""
    machine = machine_service.get_machine(machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    data = machine_service.get_machine_data(machine_id)
    if not data:
        raise HTTPException(status_code=404, detail="No current data available for machine")
    
    # Calculate anomaly score if not already done
    if data.anomaly_score is None:
        data.anomaly_score = anomaly_detector.calculate_anomaly_score(machine, data)
    
    # Get AI analysis
    ai_analysis = await anomaly_detector.analyze_anomaly_with_ai(machine, data, data.anomaly_score)
    
    # Create alert if warranted
    alert = anomaly_detector.create_anomaly_alert(machine, data, data.anomaly_score, ai_analysis)
    
    return {
        "machine_id": machine_id,
        "anomaly_score": data.anomaly_score,
        "ai_analysis": ai_analysis,
        "alert_created": alert is not None,
        "alert": alert.dict() if alert else None
    }