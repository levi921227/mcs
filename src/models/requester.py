from .node import Node
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

class Requester(Node):
    def create_task(self, task_description: str, reward_amount: int) -> Dict[str, Any]:
        """創建任務並指定獎勵金額"""
        try:
            if reward_amount <= 0:
                raise ValueError(f"獎勵金額必須為正數: {reward_amount}")
            if reward_amount > self.s_coin:
                raise ValueError(f"Requester {self.id} 沒有足夠的 R-coin (擁有: {self.s_coin}, 獎勵: {reward_amount})")
            
            # 扣除獎勵金額
            self.update_coins(s_coin_change=-reward_amount)
            
            return {
                "requester_id": self.id,
                "task_description": task_description,
                "reward_amount": reward_amount,
                "timestamp": datetime.now().isoformat()
            }
        except ValueError as e:
            logger.warning(str(e))
            return {}

    def to_dict(self) -> Dict[str, Any]:
        """將請求者轉為字典"""
        return {
            "id": self.id,
            "r_coin": self.r_coin,
            "s_coin": self.s_coin,
            "history": self.history
        } 