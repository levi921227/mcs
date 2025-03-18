import hashlib
import json
from typing import Dict, List, Any

class Block:
    def __init__(self, index: int, transactions: List[Dict], timestamp: str, previous_hash: str, verifier_id: int):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.verifier_id = verifier_id
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        """計算區塊的哈希值"""
        block_string = json.dumps({
            "index": self.index,
            "transactions": self.transactions,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "verifier_id": self.verifier_id
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """將區塊轉為字典"""
        return {
            "index": self.index,
            "transactions": self.transactions,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "verifier_id": self.verifier_id,
            "hash": self.hash
        } 