import socket
import struct
import logging
from typing import Optional, Dict, Any

class PNIOCM:
    """PNIO-CM协议实现"""
    PNIO_PORT = 34964
    
    def __init__(self, ip_address: str):
        self.ip = ip_address
        self.socket = None
        self.ar_ref = None
        self.logger = logging.getLogger('PNIOCM')
        
    def connect(self) -> bool:
        """建立PNIO-CM连接"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(5.0)
            
            # 构建Connect请求
            connect_req = self._build_connect_request()
            self.socket.sendto(connect_req, (self.ip, self.PNIO_PORT))
            
            # 接收响应
            data, _ = self.socket.recvfrom(1024)
            self.ar_ref = self._parse_connect_response(data)
            
            return True
            
        except Exception as e:
            self.logger.error(f"PNIO-CM连接失败: {str(e)}")
            return False
    
    def get_device_info(self) -> Optional[Dict[str, Any]]:
        """获取设备信息"""
        try:
            if not self.connect():
                return None
                
            device_info = {}
            
            # 读取IM0数据
            im0_data = self.read_record(0xAFF0)
            if im0_data:
                device_info['im0'] = self._parse_im0_data(im0_data)
            
            # 读取端口信息
            port_data = self.read_record(0xF001)
            if port_data:
                device_info['ports'] = self._parse_port_data(port_data)
            
            return device_info
            
        except Exception as e:
            self.logger.error(f"获取设备信息失败: {str(e)}")
            return None
        finally:
            self.disconnect()
            
    def read_record(self, index: int) -> Optional[bytes]:
        """读取记录数据"""
        try:
            if not self.ar_ref:
                return None
                
            # 构建Read请求
            read_req = self._build_read_request(index)
            self.socket.sendto(read_req, (self.ip, self.PNIO_PORT))
            
            # 接收响应
            data, _ = self.socket.recvfrom(1024)
            return self._parse_read_response(data)
            
        except Exception as e:
            self.logger.error(f"读取记录失败: {str(e)}")
            return None
            
    def disconnect(self):
        """关闭连接"""
        if self.socket:
            try:
                self.socket.close()
            except Exception:
                pass
            finally:
                self.socket = None
                self.ar_ref = None
