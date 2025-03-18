import json
import logging
from typing import List, Dict, Optional
from datetime import datetime
from .block import Block
from src.models.worker import Worker

logger = logging.getLogger(__name__)

class Blockchain:
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.create_genesis_block()

    def create_genesis_block(self):
        """創建創世區塊"""
        genesis_block = Block(
            index=0,
            transactions=[],
            timestamp=datetime.now().isoformat(),
            previous_hash="0",
            verifier_id=-1  # 特殊ID表示系統創建
        )
        self.chain.append(genesis_block)
        logger.info("創世區塊已創建")

    def add_transaction(self, transaction: Dict[str, any]):
        """添加交易到待處理列表"""
        self.pending_transactions.append(transaction)

    def add_block(self, verifier: Worker) -> Optional[Block]:
        """添加新區塊到區塊鏈"""
        if not self.pending_transactions:
            logger.warning("沒有待處理的交易，無法創建區塊")
            return None

        last_block = self.get_last_block()

        new_block = Block(
            index=last_block.index + 1,
            transactions=self.pending_transactions.copy(),
            timestamp=datetime.now().isoformat(),
            previous_hash=last_block.hash,
            verifier_id=verifier.id
        )

        # 驗證區塊
        if self.is_valid_block(new_block, last_block):
            self.chain.append(new_block)
            self.pending_transactions = []  # 清空待處理交易
            logger.info(f"區塊 {new_block.index} 已添加到鏈，驗證者: {verifier.id}")
            return new_block
        else:
            logger.error(f"區塊 {new_block.index} 驗證失敗，未添加到鏈")
            return None

    def is_valid_block(self, block: Block, previous_block: Block) -> bool:
        """驗證區塊有效性"""
        if block.index != previous_block.index + 1:
            logger.error(f"區塊索引無效: 預期 {previous_block.index + 1}，得到 {block.index}")
            return False

        if block.previous_hash != previous_block.hash:
            logger.error("區塊前一哈希值不匹配")
            return False

        if block.hash != block.calculate_hash():
            logger.error("區塊哈希計算錯誤")
            return False

        return True

    def get_last_block(self) -> Block:
        """獲取最後一個區塊"""
        return self.chain[-1]

    def is_valid_chain(self) -> bool:
        """驗證整個區塊鏈的有效性"""
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            if not self.is_valid_block(current, previous):
                return False

        return True

    def to_dict(self) -> List[Dict[str, any]]:
        """將區塊鏈轉為字典列表"""
        return [block.to_dict() for block in self.chain]

    def save_to_file(self, filename: str = "blockchain.json"):
        """保存區塊鏈到檔案"""
        with open(filename, 'w') as file:
            json.dump(self.to_dict(), file, indent=4)
        logger.info(f"區塊鏈已保存到 {filename}") 