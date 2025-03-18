import logging
import secrets
import json
from src.config.system_config import SystemConfig
from src.models.worker import Worker
from src.models.requester import Requester
from src.services.server import Server
from src.blockchain.blockchain import Blockchain
from src.services.quality_reputation_manager import QualityReputationManager
from src.simulation.simulator import simulate_crowdsensing
import sys
import os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

logger = logging.getLogger(__name__)


def main():
    """主函數"""
    # 系統配置
    config = SystemConfig()

    # 創建工作節點
    num_workers = 5
    workers = []
    for i in range(num_workers):
        initial_r = secrets.randbelow(config.initial_r_coin_range[1] - config.initial_r_coin_range[0] + 1) + \
                    config.initial_r_coin_range[0]
        worker = Worker(i, initial_r_coin=initial_r)
        workers.append(worker)
        logger.info(f"創建工作節點 {i}，初始 R-coin: {worker.r_coin}")

    # 創建請求者
    requester = Requester(id=num_workers, initial_s_coin=1000)  # 給予請求者較多的初始 R-coin
    logger.info(f"創建請求者 {requester.id}，初始 S-coin: {requester.r_coin}")

    # 創建服務器和區塊鏈
    server = Server(config)
    blockchain = Blockchain()
    qrm = QualityReputationManager(config)

    # 模擬多輪眾包感知
    simulation_rounds = 10
    successful_rounds = 0

    for round_num in range(1, simulation_rounds + 1):
        success = simulate_crowdsensing(blockchain, server, workers, qrm, round_num, requester)
        if success:
            successful_rounds += 1

    # 輸出結果
    logger.info(f"模擬完成: {successful_rounds}/{simulation_rounds} 輪成功")

    # 驗證區塊鏈
    if blockchain.is_valid_chain():
        logger.info("區塊鏈驗證成功")
    else:
        logger.error("區塊鏈驗證失敗")

    # 輸出結果
    print("\n區塊鏈概覽:")
    for i, block in enumerate(blockchain.chain):
        print(f"區塊 {i}: {len(block.transactions)} 筆交易, 驗證者: {block.verifier_id}")

    print("\n工作節點狀態:")
    for worker in workers:
        print(f"工作節點 {worker.id}: R-coin={worker.r_coin}, S-coin={worker.s_coin}")
    
    print(f"\n請求者狀態:")
    print(f"請求者 {requester.id}: R-coin={requester.r_coin}, S-coin={requester.s_coin}")

    # 保存區塊鏈到檔案
    blockchain.save_to_file()

    # 保存工作節點和請求者狀態
    with open("workers_state.json", 'w') as file:
        json.dump([worker.to_dict() for worker in workers], file, indent=4)
    logger.info("工作節點狀態已保存到 workers_state.json")
    
    with open("requester_state.json", 'w') as file:
        json.dump(requester.to_dict(), file, indent=4)
    logger.info("請求者狀態已保存到 requester_state.json")

    return blockchain, workers, server, requester


if __name__ == "__main__":
    main() 