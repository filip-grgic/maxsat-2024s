from solver import BinarySearchMaxSATSolver, MSU3MaxSatSolver, IHSMaxSatSolver
from typing import List, Dict
import time as time_module
import multiprocessing

def binary_task(sample):
    solver = BinarySearchMaxSATSolver(solver_name="g4", formula_file=sample)
    solver.solve()

def msu3_task(sample):
    solver = MSU3MaxSatSolver(solver_name="g4", formula_file=sample)
    solver.solve()

def ihs_task(sample):
    solver = IHSMaxSatSolver(solver_name="g4", formula_file=sample)
    solver.solve()

def run_benchmark(samples: List, times: Dict[str, List], time_limit: int = 30):
    for sample in samples:
        print(f'Running {sample} with BinarySearchMaxSATSolver')

        binary_thread = multiprocessing.Process(target=binary_task, args=(sample,))
        starttime = time_module.perf_counter()

        binary_thread.start()

        while True:
            if not binary_thread.is_alive():
                break
            if time_module.perf_counter() - starttime > time_limit:
                binary_thread.terminate()
                break
            time_module.sleep(0.1)

        duration = time_module.perf_counter() - starttime
        times['binary'].append(duration)
        print(f'Duration: {duration}')


        print(f'Running {sample} with MSU3MaxSatSolver')

        msu3_thread = multiprocessing.Process(target=msu3_task, args=(sample,))
        starttime = time_module.perf_counter()

        msu3_thread.start()

        while True:
            if not msu3_thread.is_alive():
                break
            if time_module.perf_counter() - starttime > time_limit:
                msu3_thread.terminate()
                break
            time_module.sleep(0.1)

        duration = time_module.perf_counter() - starttime
        times['binary'].append(duration)
        print(f'Duration: {duration}')



        print(f'Running {sample} with IHSMaxSatSolver')

        ihs_thread = multiprocessing.Process(target=ihs_task, args=(sample,))
        starttime = time_module.perf_counter()

        ihs_thread.start()

        while True:
            if not ihs_thread.is_alive():
                break
            if time_module.perf_counter() - starttime > time_limit:
                ihs_thread.terminate()
                break
            time_module.sleep(0.1)

        duration = time_module.perf_counter() - starttime
        times['binary'].append(duration)
        print(f'Duration: {duration}')


if __name__ == '__main__':
    samples_3sat = [f'./samples/3SAT/HG-3SAT-V250-C1000-{i}.cnf' for i in range(1, 6)]
    samples_4sat = [f'./samples/4SAT/HG-4SAT-V100-C900-{i}.cnf' for i in range(1, 6)]
    samples_5sat = [f'./samples/5SAT/HG-5SAT-V50-C900-{i}.cnf' for i in range(1, 6)]
    samples_maxcut = [f'./samples/maxcut/t{i}pm3-{1111*(i+2)}.spn.cnf' for i in range(3, 8)]

    samples = [samples_3sat, samples_4sat, samples_5sat, samples_maxcut]

    times_3sat = {'binary': [], 'msu3': [], 'ihs': []}
    times_4sat = {'binary': [], 'msu3': [], 'ihs': []}
    times_5sat = {'binary': [], 'msu3': [], 'ihs': []}
    times_maxcut = {'binary': [], 'msu3': [], 'ihs': []}

    times = [times_3sat, times_4sat, times_5sat, times_maxcut]

    for sample, time in zip(samples, times):
        run_benchmark(sample, time, time_limit=120)
        print(times)
