import logging
from typing import List
from datetime import datetime
from src.blockchain.blockchain import Blockchain
from src.services.server import Server
from src.models.worker import Worker
from src.services.quality_reputation_manager import QualityReputationManager
from src.models.requester import Requester
from src.utils.simulation_utils import simulate_task_completion, get_participants_count, select_random_participants

logger = logging.getLogger(__name__)

def simulate_crowdsensing(blockchain: Blockchain, server: Server, workers: List[Worker],
                          qrm: QualityReputationManager, task_num: int, requester: Requester,
                          lambda_param: float = 0.7):
    """
    模擬眾包感知流程
    
    參數:
        blockchain: 區塊鏈實例
        server: 服務器實例
        workers: 所有可用worker列表
        qrm: 質量聲譽管理器
        task_num: 當前任務編號
        requester: 請求者實例
        lambda_param: 泊松分佈的λ參數，控制平均參與率
    """
    logger.info(f"======== 開始第 {task_num} 輪模擬 ========")

    # Step1: 創建任務
    task_description = f"Sensor data collection task #{task_num}"
    reward_amount = 20  # 設定任務獎勵金額
    task_info = requester.create_task(task_description, reward_amount)
    
    if not task_info:
        logger.warning("任務創建失敗，跳過此輪")
        return False
        
    task_id = server.broadcast_task(
        task_data=task_description,
        requester_id=requester.id,
        reward_amount=reward_amount
    )

    # Step2: 選擇驗證者 (使用所有worker參與驗證者選擇，確保公平性)
    verifier = server.select_verifier(workers, blockchain)
    if not verifier:
        logger.warning("無法選擇驗證者，跳過此輪")
        return False

    # Step3: 使用泊松分佈決定有多少worker參與任務
    participant_count = get_participants_count(len(workers), lambda_param)
    participants = select_random_participants(workers, participant_count)
    
    logger.info(f"總共 {len(workers)} 個worker中，有 {len(participants)} 個參與本次任務")

    # Step4: 參與workers提交任務結果
    task_submissions = []
    for worker in participants:
        submission = worker.submit_task(task_description)
        submission["task_id"] = task_id
        task_submissions.append(submission)

    # 將提交記錄添加到待處理交易
    blockchain.add_transaction({
        "type": "task_submissions",
        "task_id": task_id,
        "submissions": task_submissions,
        "timestamp": datetime.now().isoformat()
    })

    # Step5: 評估參與者的任務完成度
    evaluations = []
    for worker in participants:
        # 使用更現實的任務完成度模擬
        task_completion = simulate_task_completion()
        evaluation = qrm.evaluate_task(worker, task_completion)
        evaluation["task_id"] = task_id
        evaluations.append(evaluation)

    # 將評估記錄添加到待處理交易
    blockchain.add_transaction({
        "type": "task_evaluations",
        "task_id": task_id,
        "evaluations": evaluations,
        "verifier_id": verifier.id,
        "timestamp": datetime.now().isoformat()
    })

    # Step6: 創建新區塊
    new_block = blockchain.add_block(verifier)

    if new_block:
        # 獎勵驗證者
        verifier_reward = 5  # 驗證者的固定獎勵
        verifier.update_coins(r_coin_change=verifier_reward)
        logger.info(f"驗證者 {verifier.id} 獲得 {verifier_reward} R-coin作為獎勵")

    logger.info(f"======== 第 {task_num} 輪模擬結束 ========\n")
    return True 