from typing import Dict, Any
from src.models.worker import Worker
from src.config.system_config import SystemConfig
from datetime import datetime

class QualityReputationManager:
    def __init__(self, config: SystemConfig):
        self.config = config

    def evaluate_task(self, worker: Worker, task_completion_degree: float) -> Dict[str, Any]:
        """評估任務完成度並更新工作者的聲譽"""
        initial_r = worker.r_coin

        # 根據任務完成度獎勵或懲罰
        if task_completion_degree > self.config.min_completion_for_reward:
            r_coin_change = self.config.reward_amount
            status = "rewarded"
        elif task_completion_degree < self.config.max_completion_for_punish:
            r_coin_change = -self.config.punish_amount
            status = "punished"
        else:
            r_coin_change = 0
            status = "neutral"

        # 更新工作者的代幣
        changes = worker.update_coins(r_coin_change=r_coin_change)

        # 記錄評估結果
        evaluation_record = {
            "worker_id": worker.id,
            "task_completion": task_completion_degree,
            "status": status,
            "r_coin_before": initial_r,
            "r_coin_after": worker.r_coin,
            "r_coin_change": changes["r_coin_change"],
            "timestamp": datetime.now().isoformat()
        }

        return evaluation_record 