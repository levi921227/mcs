import logging
from typing import Dict

logger = logging.getLogger(__name__)

class Node:
    def __init__(self, id: int, initial_r_coin: int = 0, initial_s_coin: int = 0):
        self.id = id
        self.r_coin = initial_r_coin
        self.s_coin = initial_s_coin
        self.history = []  # 記錄歷史

    def declare_r_coin(self, amount: int) -> int:
        """宣告R-coin數量"""
        try:
            if amount <= 0:
                raise ValueError(f"宣告金額必須為正數: {amount}")
            if amount > self.r_coin:
                raise ValueError(f"Node {self.id} 沒有足夠的 R-coin (擁有: {self.r_coin}, 宣告: {amount}).")
            return amount
        except ValueError as e:
            logger.warning(str(e))
            return 0

    def update_coins(self, r_coin_change: int = 0, s_coin_change: int = 0) -> Dict[str, int]:
        """更新節點幣值"""
        old_r = self.r_coin
        old_s = self.s_coin

        self.r_coin = max(0, self.r_coin + r_coin_change)
        self.s_coin = max(0, self.s_coin + s_coin_change)

        changes = {
            "r_coin_change": self.r_coin - old_r,
            "s_coin_change": self.s_coin - old_s
        }

        record = f"R-coin: {old_r} -> {self.r_coin}, S-coin: {old_s} -> {self.s_coin}"
        self.history.append(record)
        return changes 