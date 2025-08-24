import os
from datetime import datetime
from typing import List, Optional
from openai import OpenAI
from models.machine import Machine, MachineData
from models.anomaly import AnomalyAlert
from services.llm_service import LLMService
import uuid

class AnomalyDetector:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"
        self.llm_service = LLMService()
        
    def calculate_anomaly_score(self, machine: Machine, data: MachineData) -> float:
        ranges = machine.normal_ranges
        scores = []
        
        metrics = {
            'temperature': (data.temperature, ranges.temperature),
            'pressure': (data.pressure, ranges.pressure),
            'vibration': (data.vibration, ranges.vibration),
            'rpm': (data.rpm, ranges.rpm),
            'power_consumption': (data.power_consumption, ranges.power_consumption)
        }
        
        for value, range_obj in metrics.values():
            range_size = range_obj.max - range_obj.min
            center = (range_obj.max + range_obj.min) / 2
            
            if range_obj.min <= value <= range_obj.max:
                distance_from_center = abs(value - center)
                score = (distance_from_center / (range_size / 2)) * 0.3
            else:
                if value < range_obj.min:
                    excess = range_obj.min - value
                else:
                    excess = value - range_obj.max
                score = min(1.0, 0.5 + (excess / range_size))
            
            scores.append(score)
        
        return sum(scores) / len(scores)
    
    async def analyze_anomaly_with_ai(self, machine: Machine, data: MachineData, 
                                    anomaly_score: float) -> Optional[str]:
        if anomaly_score < 0.3:
            return None
            
        try:
            prompt = f"""
            Analyze this industrial machine anomaly and provide a structured response:
            
            Machine: {machine.name} ({machine.type.value})
            Current readings:
            - Temperature: {data.temperature:.1f}°C (normal: {machine.normal_ranges.temperature.min}-{machine.normal_ranges.temperature.max})
            - Pressure: {data.pressure:.0f} PSI (normal: {machine.normal_ranges.pressure.min}-{machine.normal_ranges.pressure.max})
            - Vibration: {data.vibration:.2f} mm/s (normal: {machine.normal_ranges.vibration.min}-{machine.normal_ranges.vibration.max})
            - RPM: {data.rpm:.0f} (normal: {machine.normal_ranges.rpm.min}-{machine.normal_ranges.rpm.max})
            - Power: {data.power_consumption:.1f} kW (normal: {machine.normal_ranges.power_consumption.min}-{machine.normal_ranges.power_consumption.max})
            
            Anomaly Score: {anomaly_score:.2f}/1.0
            
            Please provide your analysis in this format:
            
            **Issue**: [Brief description of the problem]
            
            **Cause**: [Most likely cause of the anomaly]
            
            **Risk**: [Potential consequences if not addressed]
            
            **Action**: [Immediate recommended actions]
            
            Keep each section to 1-2 sentences maximum.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert industrial maintenance engineer. Provide clear, structured analysis using the exact format requested."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            # Format the response for better readability
            raw_content = response.choices[0].message.content.strip()
            cleaned_content = self.llm_service.clean_text_formatting(raw_content)
            return cleaned_content
            
        except Exception as e:
            print(f"Error in AI analysis: {e}")
            return f"**Issue**: Anomaly detected with score {anomaly_score:.2f}\n**Action**: Manual inspection recommended."
    
    def create_anomaly_alert(self, machine: Machine, data: MachineData, 
                           anomaly_score: float, ai_analysis: Optional[str] = None) -> Optional[AnomalyAlert]:
        """Create an anomaly alert if conditions warrant it"""
        if anomaly_score < 0.3:  # Only create alerts for anomalies above 30%
            return None
        
        # Determine severity
        if anomaly_score >= 0.8:
            severity = "high"
        elif anomaly_score >= 0.6:
            severity = "medium"
        else:
            severity = "low"
        
        # Find which metric is most out of range
        ranges = machine.normal_ranges
        deviations = {
            'temperature': self._calculate_deviation(data.temperature, ranges.temperature),
            'pressure': self._calculate_deviation(data.pressure, ranges.pressure),
            'vibration': self._calculate_deviation(data.vibration, ranges.vibration),
            'rpm': self._calculate_deviation(data.rpm, ranges.rpm),
            'power_consumption': self._calculate_deviation(data.power_consumption, ranges.power_consumption)
        }
        
        worst_metric = max(deviations.items(), key=lambda x: x[1])
        metric_name, deviation = worst_metric
        
        # Generate message
        ranges_dict = {
            'temperature': ranges.temperature,
            'pressure': ranges.pressure,
            'vibration': ranges.vibration,
            'rpm': ranges.rpm,
            'power_consumption': ranges.power_consumption
        }
        
        range_obj = ranges_dict[metric_name]
        value = getattr(data, metric_name)
        
        message = f"{metric_name.replace('_', ' ').title()} anomaly detected: {value:.2f} (normal: {range_obj.min}-{range_obj.max})"
        
        return AnomalyAlert(
            id=str(uuid.uuid4()),
            machine_id=machine.id,
            severity=severity,
            message=message,
            metric=metric_name,
            value=value,
            expected_range=f"{range_obj.min}-{range_obj.max}",
            timestamp=datetime.now(),
            ai_analysis=ai_analysis
        )
    
    def _calculate_deviation(self, value: float, range_obj) -> float:
        """Calculate how much a value deviates from normal range"""
        if range_obj.min <= value <= range_obj.max:
            return 0.0
        elif value < range_obj.min:
            return (range_obj.min - value) / (range_obj.max - range_obj.min)
        else:
            return (value - range_obj.max) / (range_obj.max - range_obj.min)