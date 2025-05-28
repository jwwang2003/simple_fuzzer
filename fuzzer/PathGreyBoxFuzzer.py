import time
from typing import List, Tuple, Any, Set
from utils.Seed import Seed
from runner.Runner import Runner

from fuzzer.GreyBoxFuzzer import GreyBoxFuzzer
from schedule.PathPowerSchedule import PathPowerSchedule
from runner.FunctionCoverageRunner import FunctionCoverageRunner
from utils.Coverage import Location


class PathGreyBoxFuzzer(GreyBoxFuzzer):
    """Count how often individual paths are exercised."""

    def __init__(self, seeds: List[str], schedule: PathPowerSchedule, is_print: bool, seed_directory: str = './seeds'):
        super().__init__(seeds, schedule, is_print, seed_directory=seed_directory)

        # TODO
        self.start_time = time.time()
        self.last_new_path_time = self.start_time
        self.total_paths = 0
        self.path_coverage: Set[frozenset[Location]] = set()
        self._is_print = is_print

        print("""
┌───────────────────────┬───────────────────────┬───────────────────────┬───────────────────┬───────────────────┬────────────────┬───────────────────┐
│        Run Time       │     Last New Path     │    Last Uniq Crash    │    Total Execs    │    Total Paths    │  Uniq Crashes  │   Covered Lines   │
├───────────────────────┼───────────────────────┼───────────────────────┼───────────────────┼───────────────────┼────────────────┼───────────────────┤""")

    def print_stats(self):
        def format_seconds(seconds):
            hours = int(seconds) // 3600
            minutes = int(seconds % 3600) // 60
            remaining_seconds = int(seconds) % 60
            return f"{hours:02d}:{minutes:02d}:{remaining_seconds:02d}"

        template = """│{runtime}│{path_time}│{crash_time}│{total_exec}│{total_path}│{uniq_crash}│{covered_line}│
├───────────────────────┼───────────────────────┼───────────────────────┼───────────────────┼───────────────────┼────────────────┼───────────────────┤"""
        template = template.format(runtime=format_seconds(time.time() - self.start_time).center(23),
                                   path_time="".center(23),
                                   crash_time=format_seconds(self.last_crash_time - self.start_time).center(23),
                                   total_exec=str(self.total_execs).center(19),
                                   total_path="".center(19),
                                   uniq_crash=str(len(set(self.crash_map.values()))).center(16),
                                   covered_line=str(len(self.covered_line)).center(19))
        print(template)

    def run(self, runner: FunctionCoverageRunner) -> Tuple[Any, str]:  # type: ignore
        """Inform scheduler about path frequency"""
        result, outcome = super().run(runner)

        # TODO
        current_path = frozenset(runner.coverage())
        
        # Check for new path coverage
        if current_path not in self.path_coverage:
            self.path_coverage.add(current_path)
            self.total_paths += 1
            self.last_new_path_time = time.time()
            
            # Only add to population if it's a passing input
            if outcome == Runner.PASS:
                seed = Seed(self.inp, runner.coverage())
                self.population.append(seed)
    
        return result, outcome
