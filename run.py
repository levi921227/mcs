#!/usr/bin/env python
import os
import sys

# 將當前目錄添加到 Python 的模組搜索路徑中
current_dir = os.path.abspath(os.path.dirname(__file__))
print(current_dir)
sys.path.insert(0, current_dir)

# 設置日誌
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    # 執行 main.py
    from src.simulation.main import main
    
    if __name__ == "__main__":
        logger.info("開始執行模擬...")
        result = main()
        logger.info("模擬已完成!")
except ImportError as e:
    logger.error(f"導入錯誤: {e}")
    print(f"\n當前Python路徑: {sys.path}")
    print(f"當前工作目錄: {os.getcwd()}")
    sys.exit(1)
except Exception as e:
    logger.error(f"執行錯誤: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1) 