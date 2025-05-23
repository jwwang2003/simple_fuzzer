from typing import Dict, List, Sequence
import hashlib
import pickle

from schedule.PowerSchedule import PowerSchedule
from utils.Seed import Seed
from utils.Coverage import Coverage, Location


class CoveragePowerSchedule(PowerSchedule):
    """
    A PowerSchedule that assigns energy based on the novelty of execution paths,
    measured by coverage hashes and their observed frequencies.
    """

    def __init__(self) -> None:
        super().__init__()
        # Map from path hash to how many times it's been seen
        self._path_frequency: Dict[str, int] = {}
        # Map from path hash to its computed novelty score (1 / frequency)
        self._novelty_scores: Dict[str, float] = {}

    @staticmethod
    def _get_path_id(coverage: Sequence[Location]) -> str:
        """
        Generate a consistent MD5 hash for a sequence of coverage locations.
        """
        # Sort coverage to ensure order-independence, then pickle
        data = pickle.dumps(sorted(coverage))
        return hashlib.md5(data).hexdigest()

    def _record_path(self, path_id: str) -> None:
        """
        Update internal frequency and novelty score for the given path ID.
        """
        count = self._path_frequency.get(path_id, 0) + 1
        self._path_frequency[path_id] = count
        # Novelty score decays as frequency increases
        self._novelty_scores[path_id] = 1.0 / count

    def assign_energy(self, population: List[Seed]) -> None:
        """
        Assigns energy to each seed proportional to the novelty of its execution path.
        New or rare paths yield higher energy; frequent paths yield lower energy.
        """
        for seed in population:
            coverage = seed.load_coverage()
            path_id = self._get_path_id(coverage)

            # If this path hasn't been recorded yet, count it now
            if path_id not in self._novelty_scores:
                self._record_path(path_id)

            # Assign the precomputed novelty score
            seed.energy = self._novelty_scores[path_id]
