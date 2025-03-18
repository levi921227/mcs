import hashlib
import secrets
import logging
from datetime import datetime
from typing import List, Dict, Optional
from src.models.worker import Worker
from src.config.system_config import SystemConfig

logger = logging.getLogger(__name__)

class Server:
    def __init__(self, config: SystemConfig):
        self.tasks = []
        self.config = config
        self.transactions = []

    def broadcast_task(self, task_data: str, requester_id: int, reward_amount: int) -> str:
        """廣播任務並生成任務ID"""
        task_id = hashlib.sha256(f"{task_data}{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        task_info = {
            "task_id": task_id,
            "task_data": task_data,
            "requester_id": requester_id,
            "reward_amount": reward_amount,
            "timestamp": datetime.now().isoformat()
        }
        self.tasks.append(task_info)
        logger.info(f"任務廣播: ID={task_id}, 請求者={requester_id}, 獎勵={reward_amount}")
        return task_id

    def _calculate_selection_probabilities(self, nodes: List[Worker], total_declared_r: int) -> Dict[int, float]:
        """計算每個節點被選為驗證者的概率"""
        if total_declared_r == 0:
            return {node.id: 0 for node in nodes}

        return {node.id: node.s_coin / max(1, sum(n.s_coin for n in nodes)) for node in nodes}

    def select_verifier(self, nodes: List[Worker], blockchain) -> Optional[Worker]:
        """選擇驗證者 - 改進的算法"""
        if not nodes:
            logger.warning("沒有可用的工作節點")
            return None

        # 節點宣告R-coin
        declarations = {}
        total_declared_r = 0

        for node in nodes:
            # 使用更安全的隨機數生成
            max_declare = min(node.r_coin, 100)  # 限制最大宣告量
            amount_to_declare = secrets.randbelow(max_declare + 1) if max_declare > 0 else 0
            declared_amount = node.declare_r_coin(amount_to_declare)

            if declared_amount > 0:
                declarations[node.id] = declared_amount
                total_declared_r += declared_amount

        if total_declared_r == 0:
            logger.warning("沒有節點宣告R-coin，無法選擇驗證者")
            return None

        # 更新幣值 - 將狀態變更與選擇邏輯分離
        transaction_records = []
        for node in nodes:
            if node.id in declarations:
                declared_r = declarations[node.id]
                r_coin_change = -declared_r
                s_coin_change = self.config.system_s_coin * (declared_r / total_declared_r)

                coin_changes = node.update_coins(r_coin_change, s_coin_change)

                transaction_records.append({
                    "type": "verifier_selection",
                    "node_id": node.id,
                    "declared_r": declared_r,
                    "r_coin_change": coin_changes["r_coin_change"],
                    "s_coin_change": coin_changes["s_coin_change"],
                    "timestamp": datetime.now().isoformat()
                })

        # 記錄交易
        self.transactions.extend(transaction_records)

        # 基於當前S-coin和安全隨機數選擇驗證者
        probabilities = self._calculate_selection_probabilities(nodes, total_declared_r)

        # 生成安全的隨機哈希
        selection_random = secrets.token_hex(16)

        # 將每個節點的S-coin和隨機數結合生成一個選擇值
        selection_values = {}
        for node in nodes:
            node_random = hashlib.sha256(f"{selection_random}{node.id}{node.s_coin}".encode()).hexdigest()
            # 將哈希轉為浮點數，並加上基於S-coin的權重
            hash_value = int(node_random, 16) / (2 ** 256)  # 標準化哈希值
            weighted_value = hash_value * probabilities.get(node.id, 0)
            selection_values[node.id] = weighted_value

        # 選擇最高值的節點
        selected_id = max(selection_values, key=selection_values.get)
        selected_node = next((node for node in nodes if node.id == selected_id), None)

        if selected_node:
            logger.info(f"已選擇驗證者: Node {selected_node.id} (S-coin: {selected_node.s_coin})")

        return selected_node 