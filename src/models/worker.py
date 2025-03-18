from .node import Node
import hashlib
from datetime import datetime
from typing import Dict, Any

class Worker(Node):
    def submit_task(self, data: str) -> Dict[str, Any]:
        """提交任務並生成記錄"""
        task_hash = hashlib.sha256(data.encode('utf-8')).hexdigest()
        timestamp = datetime.now().isoformat()
        signature = hashlib.sha256(f"{self.id}{task_hash}{timestamp}".encode()).hexdigest()

        return {
            "worker_id": self.id,
            "task_hash": task_hash,
            "timestamp": timestamp,
            "signature": signature
        }

    def to_dict(self) -> Dict[str, Any]:
        """將工作節點轉為字典"""
        return {
            "id": self.id,
            "r_coin": self.r_coin,
            "s_coin": self.s_coin,
            "history": self.history
        } 