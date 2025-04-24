import random
import numpy as np

def simulate_task_completion() -> float:
    """模擬任務完成度，較現實的實現"""
    # 大多數任務完成得相當好，但有些可能有問題
    # 使用beta分布生成更真實的完成度分布
    # 偏向高完成度但有一定變化
    return min(1.0, max(0.0, random.betavariate(5, 1.5)))

def get_participants_count(total_workers: int, lambda_param: float = 0.7) -> int:
    """
    使用泊松分佈決定參與任務的worker數量
    
    參數:
        total_workers: 總可用worker數量
        lambda_param: 泊松分佈的λ參數，控制平均參與率 (0-1之間)
    
    返回:
        參與任務的worker數量
    """
    # 計算期望參與者人數 (lambda * total_workers)
    expected_count = lambda_param * total_workers
    
    # 使用泊松分佈生成實際參與人數
    count = np.random.poisson(expected_count)
    
    # 確保數量不超過可用worker總數且至少有1人參與
    return max(1, min(count, total_workers))

def select_random_participants(workers_list, count):
    """
    從worker列表中隨機選擇指定數量的參與者
    
    參數:
        workers_list: 所有可用worker的列表
        count: 要選擇的worker數量
        
    返回:
        選中的worker列表
    """
    if count >= len(workers_list):
        return workers_list.copy()
    
    return random.sample(workers_list, count) 