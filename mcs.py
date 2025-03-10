import hashlib
import secrets
import logging
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
import json

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# 系統配置類
@dataclass
class SystemConfig:
    reward_amount: int = 10
    punish_amount: int = 2
    min_completion_for_reward: float = 0.8
    max_completion_for_punish: float = 0.5
    system_s_coin: int = 100
    initial_r_coin_range: Tuple[int, int] = (50, 100)


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


class Server:
    def __init__(self, config: SystemConfig):
        self.tasks = []
        self.config = config
        self.transactions = []

    def broadcast_task(self, task_data: str) -> str:
        """廣播任務並生成任務ID"""
        task_id = hashlib.sha256(f"{task_data}{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        task_info = {
            "task_id": task_id,
            "task_data": task_data,
            "timestamp": datetime.now().isoformat()
        }
        self.tasks.append(task_info)
        logger.info(f"任務廣播: ID={task_id}")
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
        # 使用加權隨機選擇而不是簡單的最大值
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

    def add_transaction(self, transaction: Dict[str, Any]):
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

    def to_dict(self) -> List[Dict[str, Any]]:
        """將區塊鏈轉為字典列表"""
        return [block.to_dict() for block in self.chain]

    def save_to_file(self, filename: str = "blockchain.json"):
        """保存區塊鏈到檔案"""
        with open(filename, 'w') as file:
            json.dump(self.to_dict(), file, indent=4)
        logger.info(f"區塊鏈已保存到 {filename}")


def simulate_task_completion() -> float:
    """模擬任務完成度，較現實的實現"""
    # 大多數任務完成得相當好，但有些可能有問題
    # 使用beta分布生成更真實的完成度分布
    import random
    # 偏向高完成度但有一定變化
    return min(1.0, max(0.0, random.betavariate(5, 1.5)))


def simulate_crowdsensing(blockchain: Blockchain, server: Server, workers: List[Worker],
                          qrm: QualityReputationManager, task_num: int):
    """模擬眾包感知流程"""
    logger.info(f"======== 開始第 {task_num} 輪模擬 ========")

    # Step1: 創建任務
    task_data = f"Sensor data collection task #{task_num}"
    task_id = server.broadcast_task(task_data)

    # Step2: 選擇驗證者
    verifier = server.select_verifier(workers, blockchain)
    if not verifier:
        logger.warning("無法選擇驗證者，跳過此輪")
        return False

    # Step3: 提交任務結果
    task_submissions = []
    for worker in workers:
        submission = worker.submit_task(task_data)
        submission["task_id"] = task_id
        task_submissions.append(submission)

    # 將提交記錄添加到待處理交易
    blockchain.add_transaction({
        "type": "task_submissions",
        "task_id": task_id,
        "submissions": task_submissions,
        "timestamp": datetime.now().isoformat()
    })

    # Step4: 任務評估
    evaluations = []
    for worker in workers:
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

    # Step5: 創建新區塊
    new_block = blockchain.add_block(verifier)

    if new_block:
        # 獎勵驗證者
        verifier_reward = 5  # 驗證者的固定獎勵
        verifier.update_coins(r_coin_change=verifier_reward)
        logger.info(f"驗證者 {verifier.id} 獲得 {verifier_reward} R-coin作為獎勵")

    logger.info(f"======== 第 {task_num} 輪模擬結束 ========\n")
    return True


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

    # 創建服務器和區塊鏈
    server = Server(config)
    blockchain = Blockchain()
    qrm = QualityReputationManager(config)

    # 模擬多輪眾包感知
    simulation_rounds = 10
    successful_rounds = 0

    for round_num in range(1, simulation_rounds + 1):
        success = simulate_crowdsensing(blockchain, server, workers, qrm, round_num)
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

    # 保存區塊鏈到檔案
    blockchain.save_to_file()

    # 保存工作節點狀態
    with open("workers_state.json", 'w') as file:
        json.dump([worker.to_dict() for worker in workers], file, indent=4)
    logger.info("工作節點狀態已保存到 workers_state.json")

    return blockchain, workers, server


if __name__ == "__main__":
    main()