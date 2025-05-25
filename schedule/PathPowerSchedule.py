from typing import Dict, Sequence
from collections import defaultdict

from schedule.PowerSchedule import PowerSchedule
from utils.Seed import Seed
from utils.Coverage import Location


class PathPowerSchedule(PowerSchedule):

    def __init__(self, exponent: float = 1.0) -> None:
        super().__init__()
        # TODO
        self.path_frequency: Dict[frozenset[Location], int] = defaultdict(int)
        self.exponent = exponent
        

    def assign_energy(self, population: Sequence[Seed]) -> None:
        """Assign exponential energy inversely proportional to path frequency"""
        # TODO
        for seed in population:
            path_key = frozenset(seed.coverage)
            self.path_frequency[path_key] += 1

        # 根据路径频率分配能量（频率越低能量越高）
        for seed in population:
            path_key = frozenset(seed.coverage)
            frequency = self.path_frequency[path_key]
            # 使用反比例函数分配能量，加入指数控制偏向程度
            seed.energy = 1.0 / (frequency ** self.exponent)
