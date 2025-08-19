import json
import os
from typing import List, Dict, Optional
from datetime import datetime
from models.machine import Machine, MachineData, MachineStatus, MachineDataResponse

class MachineService:
    def __init__(self):
        self.machines: Dict[str, Machine] = {}
        self.machine_data: Dict[str, MachineData] = {}
        self._load_machine_configs()
    
    def _load_machine_configs(self):
        """Load machine configurations from config file"""
        config_path = os.path.join(os.path.dirname(__file__), '../../../config/machine_configs.json')
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                for machine_config in config['machines']:
                    machine = Machine(**machine_config)
                    self.machines[machine.id] = machine
        except FileNotFoundError:
            print(f"Machine config file not found at {config_path}")
        except Exception as e:
            print(f"Error loading machine configs: {e}")
    
    def get_all_machines(self) -> List[Machine]:
        """Get all configured machines"""
        return list(self.machines.values())
    
    def get_machine(self, machine_id: str) -> Optional[Machine]:
        """Get a specific machine by ID"""
        return self.machines.get(machine_id)
    
    def update_machine_data(self, machine_id: str, data: MachineData):
        """Update machine data"""
        self.machine_data[machine_id] = data
    
    def get_machine_data(self, machine_id: str) -> Optional[MachineData]:
        """Get current machine data"""
        return self.machine_data.get(machine_id)
    
    def get_all_machine_data(self) -> List[MachineDataResponse]:
        """Get current data for all machines"""
        responses = []
        for machine_id, machine in self.machines.items():
            data = self.machine_data.get(machine_id)
            if data:
                response = MachineDataResponse(
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
                responses.append(response)
        return responses
    
    def get_machine_status(self, machine_id: str) -> MachineStatus:
        """Get current status of a machine"""
        data = self.machine_data.get(machine_id)
        return data.status if data else MachineStatus.OFFLINE