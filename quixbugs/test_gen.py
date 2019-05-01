import sys
import importlib
import random
import signal
from neighbour import get_neighbours
import types

TIMELIMIT = 1

class TIMEOUT(Exception):
    pass

def handler(signum, frame):
    raise TIMEOUT

TARGETS = [
    'next_permutation',
    'lis',
    'mergesort',
    'bucketsort',
    'shunting_yard',
    'hanoi',
    'gcd',
    'to_base',
    'possible_change',
    'bitcount',
    'wrap',
]

TRY = 1000

def gen(correct, buggy, base):
    signal.signal(signal.SIGALRM, handler)
    #print(correct(*base))
    #print(buggy(*base))
    passing = []
    for i in range(TRY):
        neighbours = get_neighbours(base, 2, 0.001)
        for neighbour in neighbours:
            try:
                signal.alarm(TIMELIMIT)
                correct_result = correct(*neighbour)
                signal.alarm(TIMELIMIT)
                buggy_result = buggy(*neighbour)
                if correct_result == buggy_result:
                    print([neighbour, correct_result])
                    passing.append(neighbour)
                    return neighbour
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            except:
                pass
        base = random.choice(neighbours)

def run(module_name):
    correct_module = importlib.import_module("correct_python_programs.{}".format(module_name))
    correct_func = correct_module.__dict__[module_name]
    buggy_module = importlib.import_module("python_programs.{}".format(module_name))
    buggy_func = buggy_module.__dict__[module_name]
    tests = []
    with open("json_testcases/{}.json".format(module_name), 'r') as f:
        for l in f.readlines():
            if l.strip():
                tests.append(eval(l.replace('true', 'True').replace('false', 'False')))
    base = tests[0][0]
    if not isinstance(base, list):
        base = [base]
    print(module_name)
    result = gen(correct_func, buggy_func, base)
    #if result:
    #    print(module_name, result)

if __name__ == "__main__":
    for target in TARGETS:
        run(target)
    #module_name = sys.argv[1]
