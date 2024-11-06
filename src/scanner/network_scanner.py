import asyncio
import logging
from typing import Dict, Optional
from datetime import datetime

from src.protocols.dcp import DCPScanner
from src.protocols.pnio_cm import PNIOCM
from src.protocols.lldp import LLDPScanner
from src.models.device import Device, Port

class NetworkScanner:
    """网络扫描器主类"""
    
    def __init__(self):
        self.dcp = DCPScanner()
        self.lldp = LLDPScanner()
        self.logger = logging.getLogger('NetworkScanner')
        
    async def scan_network(self) -> Optional[Dict]:
        """执行完整的网络扫描"""
        try:
            self.logger.info("开始DCP设备发现...")
            discovered_devices = self.dcp.discover_devices()
            
            devices = []
            for dev in discovered_devices:
                if 'ip_address' in dev:
                    self.logger.info(f"正在扫描设备: {dev['ip_address']}")
                    pnio = PNIOCM(dev['ip_address'])
                    device_info = pnio.get_device_info()
                    if device_info:
                        dev.update(device_info)
                        devices.append(self._create_device_model(dev))
            
            self.logger.info("开始拓扑发现...")
            topology = await self.lldp.discover_topology(devices)
            
            return {
                'devices': [device.to_dict() for device in devices],
                'topology': topology,
                'scan_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"网络扫描失败: {str(e)}")
            return None
            
    def _create_device_model(self, device_data: dict) -> Device:
        """创建设备模型实例"""
        ports = []
        if 'ports' in device_data:
            for port_data in device_data['ports']:
                ports.append(Port(**port_data))
        
        return Device(
            name=device_data.get('name', ''),
            ip_address=device_data.get('ip_address', ''),
            mac_address=device_data.get('mac_address', ''),
            device_type=device_data.get('device_type', ''),
            manufacturer=device_data.get('manufacturer', ''),
            serial_number=device_data.get('serial_number'),
            hardware_version=device_data.get('hardware_version'),
            software_version=device_data.get('software_version'),
            ports=ports,
            last_scan=datetime.now()
        )
