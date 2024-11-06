import asyncio
import json
import logging
from datetime import datetime
from src.scanner.network_scanner import NetworkScanner

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('output/logs/scanner.log'),
        logging.StreamHandler()
    ]
)

async def main():
    logger = logging.getLogger('main')
    scanner = NetworkScanner()
    
    logger.info("开始网络扫描...")
    result = await scanner.scan_network()
    
    if result:
        # 生成输出文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'output/reports/scan_result_{timestamp}.json'
        
        # 保存结果
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        logger.info(f"扫描完成，发现 {len(result['devices'])} 个设备")
        logger.info(f"结果已保存到: {filename}")
    else:
        logger.error("扫描失败")

if __name__ == "__main__":
    asyncio.run(main())
