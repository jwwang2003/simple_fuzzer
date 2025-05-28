import os
import time

from fuzzer.PathGreyBoxFuzzer import PathGreyBoxFuzzer
from runner.FunctionCoverageRunner import FunctionCoverageRunner
from schedule.PathPowerSchedule import PathPowerSchedule
from samples.Samples import sample1, sample2, sample3, sample4
from utils.ObjectUtils import dump_object, load_object

from utils.SeedPersister import SeedPersister
from utils.Seed import Seed


class Result:
    def __init__(self, coverage, crashes, start_time, end_time):
        self.covered_line = coverage
        self.crashes = crashes
        self.start_time = start_time
        self.end_time = end_time

    def __str__(self):
        return "Covered Lines: " + str(self.covered_line) + ", Crashes Num: " + str(self.crashes) + ", Start Time: " + str(self.start_time) + ", End Time: " + str(self.end_time)


if __name__ == "__main__":
    storage_dir = "./seedDB/corpus_4"
    persister = SeedPersister(storage_dir)

    # 加载已有 seeds 作为初始种子
    seeds = persister.load_all_seeds()
    if not seeds:
        print(f"seedDB: {storage_dir} is empty")
        # 如果目录为空，可从旧有的 corpus 加载一次性导入
        old_seeds = load_object("corpus/corpus_4")  # 只执行一次
        for data in old_seeds:
            seed = Seed(data, set(), directory=storage_dir)
            persister.save_seed(seed)
        seeds = persister.load_all_seeds()

    f_runner = FunctionCoverageRunner(sample4)
    # seeds = load_object("corpus/corpus_4")

    grey_fuzzer = PathGreyBoxFuzzer(seeds=seeds, schedule=PathPowerSchedule(5), is_print=True, seed_directory=storage_dir)
    start_time = time.time()
    grey_fuzzer.runs(f_runner, run_time=300)
    end_time = time.time()

    res = Result(grey_fuzzer.covered_line, set(grey_fuzzer.crash_map.values()), start_time, end_time)
    dump_object("_result" + os.sep + "Sample-4.pkl", res)
    print(load_object("_result" + os.sep + "Sample-4.pkl"))

    print(f'Running time: {end_time - start_time:.2f}s')
