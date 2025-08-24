from fastapi import APIRouter, HTTPException
from typing import List
from models.machine import Machine, MachineDataResponse
from services.machine_service import MachineService
from services.data_generator import DataGenerator
from services.anomaly_detector import AnomalyDetector
from services.llm_service import LLMService

router = APIRouter()

machine_service = MachineService()
data_generator = DataGenerator()
anomaly_detector = AnomalyDetector()
llm_service = LLMService()

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
    
    # Format analysis for frontend display
    formatted_analysis = None
    if ai_analysis:
        formatted_analysis = llm_service.format_response_for_display(ai_analysis)
    
    # Create alert if warranted
    alert = anomaly_detector.create_anomaly_alert(machine, data, data.anomaly_score, ai_analysis)
    
    return {
        "machine_id": machine_id,
        "anomaly_score": data.anomaly_score,
        "ai_analysis": ai_analysis,
        "formatted_analysis": formatted_analysis,
        "alert_created": alert is not None,
        "alert": alert.dict() if alert else None
    }

@router.post("/performance-report")
async def generate_performance_report():
    machines = machine_service.get_all_machines()
    machine_data_list = machine_service.get_all_machine_data()
    
    if not machine_data_list:
        return {"report": "No machine data available for analysis.", "error": True}
    
    try:
        prompt = f"""
        Generate a comprehensive performance report for the industrial facility with {len(machines)} machines:
        
        Current Status Overview:
        """
        
        for machine_data in machine_data_list:
            machine = machine_service.get_machine(machine_data.machine_id)
            prompt += f"""
        
        {machine_data.name} ({machine_data.type}):
        - Status: {machine_data.status.upper()}
        - Anomaly Score: {machine_data.anomaly_score:.1%}
        - Temperature: {machine_data.data['temperature']:.1f}°C
        - Pressure: {machine_data.data['pressure']:.0f} PSI
        - Vibration: {machine_data.data['vibration']:.2f} mm/s
        - RPM: {machine_data.data['rpm']:.0f}
        - Power: {machine_data.data['power_consumption']:.1f} kW
        """
        
        prompt += """
        
        Please provide a comprehensive facility performance report in this structured format:
        
        ## FACILITY PERFORMANCE SUMMARY
        
        **Overall Status**: [Brief overall assessment]
        
        ## KEY PERFORMANCE INDICATORS
        
        **Operational Efficiency**: [Efficiency assessment]
        **Equipment Health**: [Overall equipment condition]
        **Performance Trends**: [Notable trends or patterns]
        
        ## RISK ASSESSMENT
        
        **High Priority Issues**: [Critical items requiring immediate attention]
        **Medium Priority Items**: [Items to monitor closely]
        **Preventive Opportunities**: [Proactive maintenance suggestions]
        
        ## RECOMMENDATIONS
        
        **Immediate Actions**: [Actions needed within 24-48 hours]
        **Short-term Planning**: [Actions for next 1-2 weeks]
        **Long-term Strategy**: [Strategic recommendations]
        
        Keep each section concise and actionable for facility management.
        """
        
        response = anomaly_detector.client.chat.completions.create(
            model=anomaly_detector.model,
            messages=[
                {"role": "system", "content": "You are a senior industrial operations analyst. Provide executive reports using the exact structured format requested with proper headings and sections."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.3
        )
        
        # Format the response for better readability
        raw_report = response.choices[0].message.content.strip()
        formatted_report = llm_service.clean_text_formatting(raw_report)
        formatted_data = llm_service.format_response_for_display(formatted_report)
        
        return {
            "report": formatted_report,
            "formatted_data": formatted_data,
            "timestamp": machine_data_list[0].last_updated if machine_data_list else None
        }
        
    except Exception as e:
        return {"report": f"Unable to generate performance report: {str(e)}", "error": True}