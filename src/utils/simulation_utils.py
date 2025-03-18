import random

def simulate_task_completion() -> float:
    """模擬任務完成度，較現實的實現"""
    # 大多數任務完成得相當好，但有些可能有問題
    # 使用beta分布生成更真實的完成度分布
    # 偏向高完成度但有一定變化
    return min(1.0, max(0.0, random.betavariate(5, 1.5))) 