from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class Port:
    """端口信息模型"""
    port_id: str
    port_type: str
    port_status: str
    remote_port_id: Optional[str] = None
    remote_device_mac: Optional[str] = None

@dataclass
class Device:
    """设备信息模型"""
    name: str
    ip_address: str
    mac_address: str
    device_type: str
    manufacturer: str
    serial_number: Optional[str] = None
    hardware_version: Optional[str] = None
    software_version: Optional[str] = None
    ports: List[Port] = None
    last_scan: datetime = None
    
    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'ip_address': self.ip_address,
            'mac_address': self.mac_address,
            'device_type': self.device_type,
            'manufacturer': self.manufacturer,
            'serial_number': self.serial_number,
            'hardware_version': self.hardware_version,
            'software_version': self.software_version,
            'ports': [port.__dict__ for port in self.ports] if self.ports else None,
            'last_scan': self.last_scan.isoformat() if self.last_scan else None
        }
