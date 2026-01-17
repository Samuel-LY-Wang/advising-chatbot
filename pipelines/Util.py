import time

def time_execution(func):
    start_time = time.time()
    func()
    end_time = time.time()
    print(f"Execution time: {end_time - start_time} seconds")