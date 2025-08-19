import random
import math
from datetime import datetime
from typing import Dict
from models.machine import Machine, MachineData, MachineStatus

class DataGenerator:
    def __init__(self):
        self.time_offset = 0
        
    def generate_realistic_data(self, machine: Machine) -> MachineData:
        """Generate realistic machine data based on machine type and normal ranges"""
        ranges = machine.normal_ranges
        
        # Add some variability and trends
        self.time_offset += 1
        time_factor = math.sin(self.time_offset * 0.1) * 0.1  # Slow oscillation
        noise_factor = random.uniform(-0.05, 0.05)  # Random noise
        
        # Generate base values within normal ranges
        base_temp = (ranges.temperature.min + ranges.temperature.max) / 2
        base_pressure = (ranges.pressure.min + ranges.pressure.max) / 2
        base_vibration = (ranges.vibration.min + ranges.vibration.max) / 2
        base_rpm = (ranges.rpm.min + ranges.rpm.max) / 2
        base_power = (ranges.power_consumption.min + ranges.power_consumption.max) / 2
        
        # Apply variations
        temperature = base_temp + (base_temp * time_factor) + (base_temp * noise_factor)
        pressure = base_pressure + (base_pressure * time_factor * 0.5) + (base_pressure * noise_factor)
        vibration = base_vibration + (base_vibration * time_factor * 0.3) + (base_vibration * noise_factor)
        rpm = base_rpm + (base_rpm * time_factor * 0.2) + (base_rpm * noise_factor)
        power_consumption = base_power + (base_power * time_factor * 0.4) + (base_power * noise_factor)
        
        # Frequently introduce anomalies (80% chance for demo)
        if random.random() < 0.8:
            anomaly_type = random.choice(['temperature', 'pressure', 'vibration', 'rpm', 'power'])
            if anomaly_type == 'temperature':
                temperature = random.choice([
                    ranges.temperature.min * 0.5,  # Critically low
                    ranges.temperature.max * 1.6   # Critically high
                ])
            elif anomaly_type == 'pressure':
                pressure = random.choice([
                    ranges.pressure.min * 0.3,  # Critically low
                    ranges.pressure.max * 2.0   # Critically high
                ])
            elif anomaly_type == 'vibration':
                vibration = ranges.vibration.max * 3.0  # Extremely high vibration
            elif anomaly_type == 'rpm':
                rpm = random.choice([
                    ranges.rpm.min * 0.2,  # Critically low
                    ranges.rpm.max * 2.0   # Critically high
                ])
            elif anomaly_type == 'power':
                power_consumption = random.choice([
                    ranges.power_consumption.min * 0.1,  # Critically low
                    ranges.power_consumption.max * 2.5   # Critically high
                ])
        
        # Determine status based on values
        status = self._determine_status(machine, temperature, pressure, vibration, rpm, power_consumption)
        
        return MachineData(
            machine_id=machine.id,
            timestamp=datetime.now(),
            temperature=temperature,
            pressure=pressure,
            vibration=vibration,
            rpm=rpm,
            power_consumption=power_consumption,
            status=status
        )
    
    def _determine_status(self, machine: Machine, temp: float, pressure: float, 
                         vibration: float, rpm: float, power: float) -> MachineStatus:
        """Determine machine status based on current values"""
        ranges = machine.normal_ranges
        
        # Check for critical conditions
        critical_conditions = [
            temp < ranges.temperature.min * 0.9 or temp > ranges.temperature.max * 1.1,
            pressure < ranges.pressure.min * 0.8 or pressure > ranges.pressure.max * 1.2,
            vibration > ranges.vibration.max * 1.3,
            rpm < ranges.rpm.min * 0.8 or rpm > ranges.rpm.max * 1.2,
            power < ranges.power_consumption.min * 0.7 or power > ranges.power_consumption.max * 1.3
        ]
        
        if any(critical_conditions):
            return MachineStatus.CRITICAL
        
        # Check for warning conditions
        warning_conditions = [
            temp < ranges.temperature.min * 0.95 or temp > ranges.temperature.max * 1.05,
            pressure < ranges.pressure.min * 0.9 or pressure > ranges.pressure.max * 1.1,
            vibration > ranges.vibration.max * 1.1,
            rpm < ranges.rpm.min * 0.9 or rpm > ranges.rpm.max * 1.1,
            power < ranges.power_consumption.min * 0.85 or power > ranges.power_consumption.max * 1.15
        ]
        
        if any(warning_conditions):
            return MachineStatus.WARNING
        
        return MachineStatus.NORMAL