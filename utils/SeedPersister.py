import os
from typing import List, Set
from utils.Coverage import Location
from utils.Seed import Seed

class SeedPersister:
    def __init__(self, directory: str = './seedDB') -> None:
        self.directory = directory
        os.makedirs(directory, exist_ok=True)

    def save_seed(self, seed: Seed):
        seed.save()

    def load_all_seeds(self) -> List[Seed]:
        seeds = []
        for filename in os.listdir(self.directory):
            if filename.endswith('.data'):
                seed_id = filename[:-5]  # strip '.data'
                seed = Seed(id=seed_id, directory=self.directory)
                seeds.append(seed)
        return seeds
