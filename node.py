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


class Worker(Node):
    def submit_task(self, data):
        return hashlib.sha256(data.encode('utf-8')).hexdigest()


class Server:
    def __init__(self):
        self.tasks = []

    def broadcast_task(self, task_data):
        self.tasks.append(task_data)
        print(f"Task broadcasted: {task_data}")

    def select_verifier(self, nodes, total_r_coin, system_s_coin):
        return select_verifier_simplified(nodes, total_r_coin, system_s_coin, blockchain)


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


def generate_random_hash(s_coin_str):
    return hashlib.sha256(s_coin_str.encode('utf-8')).hexdigest()


def select_verifier_simplified(nodes, total_r_coin, system_s_coin, blockchain):
    if total_r_coin == 0:
        return None
    for node in nodes:
        declared_r = node.declare_r_coin(random.randint(0, min(100, int(node.r_coin))))
        if declared_r > 0:
            node.r_coin -= declared_r
            node.s_coin += system_s_coin * (declared_r / total_r_coin)
    random_values = [generate_random_hash(str(node.s_coin)) for node in nodes]
    return nodes[random_values.index(max(random_values))]


def qrm_simplified(node, task_completion_degree):
    reward, punish = 10, 2
    if task_completion_degree > 0.8:
        node.r_coin += reward
    elif task_completion_degree < 0.5:
        node.r_coin = max(0, node.r_coin - punish)
    node.history.append(f"Task completion {task_completion_degree}, r_coin {node.r_coin}")
    return node.r_coin


def simulate_crowdsensing(blockchain, server, workers, system_s_coin):
    # Step1 : create task
    task_data = "Sensor data from workers"
    server.broadcast_task(task_data)
    # Step2 : select verifier
    total_r_coin = sum(worker.r_coin for worker in workers)
    verifier = server.select_verifier(workers, total_r_coin, system_s_coin)
    if not verifier:
        print("No verifier selected")
        return
    # Step3 : Submit task
    task_hashes = {worker.id: worker.submit_task(task_data) for worker in workers}
    # Step4 : Verify
    for worker in workers:
        task_completion = random.random()
        qrm_simplified(worker, task_completion)
    last_block = blockchain.get_last_block()
    # Step5 : Transaction
    new_block = {
        'index': last_block['index'] + 1,
        'transactions': task_hashes,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'previous_hash': hashlib.sha256(str(last_block).encode('utf-8')).hexdigest(),
        'verifier': verifier,
    }
    # Step6 : New block
    blockchain.add_block(new_block)


num_workers, initial_r_coin, system_s_coin = 5, 100, 100
workers = [Worker(i, random.randint(50, initial_r_coin)) for i in range(num_workers)]
server, blockchain = Server(), Blockchain()

for _ in range(10):
    simulate_crowdsensing(blockchain, server, workers, system_s_coin)
    print("\n")

print("Blockchain:")
for block in blockchain.chain:
    print(block)

for worker in workers:
    print(f"Worker {worker.id} history: {worker.history}, r_coin {worker.r_coin}, s_coin {worker.s_coin}")
