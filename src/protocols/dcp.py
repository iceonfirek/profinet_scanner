import socket
import struct
import logging
from typing import List, Optional
import netifaces
from scapy.all import *

class DCPScanner:
    """DCP协议扫描器"""
    DCP_MULTICAST = "01:0e:cf:00:00:00"
    DCP_PORT = 0x8892
    
    def __init__(self):
        self.sock = None
        self.logger = logging.getLogger('DCPScanner')
        self.interface = self._get_default_interface()
        
    def _get_default_interface(self) -> str:
        """获取默认网络接口"""
        try:
            # 获取默认网关使用的接口
            gateways = netifaces.gateways()
            default_gateway = gateways['default'][netifaces.AF_INET]
            return default_gateway[1]  # 返回接口名称
        except Exception:
            # 如果获取失败，尝试找到第一个活跃的接口
            for iface in netifaces.interfaces():
                if iface != 'lo0' and netifaces.AF_INET in netifaces.ifaddresses(iface):
                    return iface
        return 'en0'  # 默认返回en0
        
    def discover_devices(self) -> List[dict]:
        """发现网络中的PROFINET设备"""
        devices = []
        try:
            # 使用scapy发送和接收数据包
            self.logger.info(f"使用网络接口: {self.interface}")
            
            # 构建DCP请求包
            eth = Ether(dst=self.DCP_MULTICAST)
            dcp = Raw(self._build_identify_request())
            
            # 发送数据包并接收响应
            ans, unans = srp(eth/dcp, iface=self.interface, timeout=2, verbose=0)
            
            # 处理响应
            for sent, received in ans:
                try:
                    device = self._parse_dcp_response(received)
                    if device:
                        # 从scapy数据包中获取MAC和IP
                        device['mac_address'] = received.src
                        if received.haslayer('IP'):
                            device['ip_address'] = received['IP'].src
                        devices.append(device)
                except Exception as e:
                    self.logger.error(f"处理响应包错误: {str(e)}")
                    
        except Exception as e:
            self.logger.error(f"DCP发现错误: {str(e)}")
            
        return devices
    
    def _build_identify_request(self) -> bytes:
        """构建DCP Identify请求包"""
        # DCP头部
        dcp_header = struct.pack('!BBHH',
            0xFE,  # ServiceID: Identify
            0x00,  # ServiceType: Request
            0x0001,  # XID
            0x0004)  # DataLength
            
        # DCP数据
        dcp_data = struct.pack('!HH',
            0x0001,  # Option: All
            0x0000)  # SubOption: All
            
        return dcp_header + dcp_data
    
    def _parse_dcp_response(self, packet) -> Optional[dict]:
        """解析DCP响应数据包"""
        try:
            # 从原始数据中提取DCP负载
            if packet.haslayer('Raw'):
                data = bytes(packet['Raw'])
            else:
                return None
                
            device = {
                'device_options': {}
            }
            
            # 跳过DCP头部(6字节)
            pos = 6
            
            # 解析DCP数据块
            while pos < len(data):
                option_type, option_length = struct.unpack('!HH', data[pos:pos+4])
                pos += 4
                
                if option_type == 0x0001:  # Device Properties
                    device['device_options'].update(
                        self._parse_device_properties(data[pos:pos+option_length]))
                
                pos += option_length
            
            return device
            
        except Exception as e:
            self.logger.error(f"解析DCP响应失败: {str(e)}")
            return None
    
    def _parse_device_properties(self, data: bytes) -> dict:
        """解析设备属性"""
        properties = {}
        pos = 0
        
        while pos < len(data):
            suboption_type, suboption_length = struct.unpack('!HH', data[pos:pos+4])
            pos += 4
            
            value = data[pos:pos+suboption_length]
            
            if suboption_type == 0x0001:  # Name of Station
                properties['name'] = value.decode('utf-8').rstrip('\x00')
            elif suboption_type == 0x0002:  # IP Parameter
                ip, subnet, gateway = struct.unpack('!4s4s4s', value[:12])
                properties['ip_address'] = socket.inet_ntoa(ip)
                properties['subnet_mask'] = socket.inet_ntoa(subnet)
                properties['gateway'] = socket.inet_ntoa(gateway)
            
            pos += suboption_length
        
        return properties
