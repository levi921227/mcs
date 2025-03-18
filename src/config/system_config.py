from dataclasses import dataclass
from typing import Tuple

@dataclass
class SystemConfig:
    reward_amount: int = 10
    punish_amount: int = 2
    min_completion_for_reward: float = 0.8
    max_completion_for_punish: float = 0.5
    system_s_coin: int = 100
    initial_r_coin_range: Tuple[int, int] = (50, 100) 