import hashlib
import random
from datetime import datetime


class Node:
    def __init__(self, id, initial_r_coin=0, initial_s_coin=0):
        self.id = id
        self.r_coin = initial_r_coin
        self.s_coin = initial_s_coin
        self.history = []  # 用於記錄歷史

    def declare_r_coin(self, amount):
        if amount > self.r_coin:
            print(f"Error: Node {self.id} doesn't have enough R-coin.")
            return 0
        return amount


class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = {
            'index': 0,
            'transactions': [],
            'timestamp': '2024-01-01 00:00:00',
            'previous_hash': '0',
            'verifier': None,
        }
        self.chain.append(genesis_block)

    def add_block(self, block):
        self.chain.append(block)
        print(f'Block added to chain, index {block["index"]} by verifier {block["verifier"].id}')

    def get_last_block(self):
        return self.chain[-1]

    def get_blockchain(self):
        return self.chain


def generate_random_hash(s_coin_str):
    hasher = hashlib.sha256()
    hasher.update(s_coin_str.encode('utf-8'))
    return hasher.hexdigest()


def select_verifier_simplified(nodes, total_r_coin, system_s_coin, blockchain):
    """簡化版的驗證者選擇機制"""
    if total_r_coin == 0:
        return None
    # S-coin 分配
    for node in nodes:
        declared_r = node.declare_r_coin(random.randint(0, min(100, int(node.r_coin))))  # 隨機聲明
        if declared_r > 0:
            node.r_coin -= declared_r
            node.s_coin += system_s_coin * (declared_r / total_r_coin)

    # 生成隨機哈希值
    random_values_for_nodes = []
    for node in nodes:
        random_values_for_nodes.append(generate_random_hash(str(node.s_coin)))

    # 選擇驗證者（簡單地選擇哈希值最大的節點）
    max_hash_index = random_values_for_nodes.index(max(random_values_for_nodes))
    selected_verifier = nodes[max_hash_index]
    return selected_verifier


def qrm_simplified(node, task_completion_degree):
    """簡化版的 QRM"""
    # 根據任務完成度更新 R-coin
    reward = 10
    punish = 2
    if task_completion_degree > 0.8:
        node.r_coin += reward
    elif task_completion_degree < 0.5:
        node.r_coin = max(0, node.r_coin - punish)
    node.history.append(f"Task complation degree {task_completion_degree}, r coin now {node.r_coin}")
    return node.r_coin


def simulate_task(blockchain, nodes, system_s_coin):
    """模擬任務流程"""
    # 1. 計算總 R-coin
    total_r_coin = sum([node.r_coin for node in nodes])

    # 2. 選擇 Verifier
    verifier = select_verifier_simplified(nodes, total_r_coin, system_s_coin, blockchain)
    if verifier is None:
        print("No verifier can be selected")
        return

    # 3. 模擬任務完成度 (每個節點都可以隨機完成任務)
    for node in nodes:
        task_completion_degree = random.random()
        qrm_simplified(node, task_completion_degree)

    # 4. 產生新的區塊
    last_block = blockchain.get_last_block()
    new_block = {
        'index': last_block['index'] + 1,
        'transactions': [],  # 簡化的交易
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'previous_hash': hashlib.sha256(str(last_block).encode('utf-8')).hexdigest(),
        'verifier': verifier,
    }
    blockchain.add_block(new_block)


# 模擬環境設定
num_nodes = 5
initial_r_coin = 100
system_s_coin = 100
nodes = [Node(id=i, initial_r_coin=random.randint(50, initial_r_coin)) for i in range(num_nodes)]
blockchain = Blockchain()

# 模擬多個區塊的生成
for i in range(10):
    simulate_task(blockchain, nodes, system_s_coin)
    print("\n")

# 輸出區塊鏈
print("Blockchain data:")
for block in blockchain.get_blockchain():
    print(block)

for node in nodes:
    print(f"Node {node.id} history:{node.history}, r coin {node.r_coin}, s coin {node.s_coin}")