#!/usr/bin/env python
import os
import sys
import argparse

# 將當前目錄添加到 Python 的模組搜索路徑中
current_dir = os.path.abspath(os.path.dirname(__file__))
print(current_dir)
sys.path.insert(0, current_dir)

# 設置日誌
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 創建資料目錄
os.makedirs('data', exist_ok=True)

def parse_arguments():
    """解析命令行參數"""
    parser = argparse.ArgumentParser(description='區塊鏈眾包感知系統模擬')
    
    parser.add_argument('-w', '--workers', type=int, default=10,
                        help='系統中的worker總數 (默認: 10)')
    
    parser.add_argument('-r', '--rounds', type=int, default=20,
                        help='模擬輪數 (默認: 20)')
    
    parser.add_argument('-l', '--lambda', type=float, dest='lambda_param', default=0.7,
                        help='泊松分佈的λ參數，控制平均參與率 (0-1之間) (默認: 0.7)')
    
    return parser.parse_args()

try:
    # 執行 main.py
    from src.simulation.main import main
    
    if __name__ == "__main__":
        args = parse_arguments()
        
        logger.info("開始執行模擬...")
        logger.info(f"參數設置: worker數量={args.workers}, 模擬輪數={args.rounds}, λ參數={args.lambda_param}")
        
        result = main(
            worker_count=args.workers,
            simulation_rounds=args.rounds,
            lambda_param=args.lambda_param
        )
        
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