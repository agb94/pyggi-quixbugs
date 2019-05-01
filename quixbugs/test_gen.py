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
    'possible_change',
    'lis',
    'mergesort',
    'bucketsort',
    'shunting_yard',
    'gcd',
    'to_base',
    'hanoi',
    'bitcount',
    'wrap',
]

TRY = 200

def is_valid_input(module_name, tinput):
    try:
        if module_name == 'next_permutation':
            #A list of unique ints
            perm = tinput[0]
            return isinstance(perm, list) and all([isinstance(i, int) for i in perm]) and len(list(set(perm))) == len(perm) and not (list(reversed(sorted(perm))) == perm)
        elif module_name == 'lis':
            arr = tinput[0]
            # The ints in arr are unique
            return isinstance(arr, list) and all([isinstance(i, int) for i in arr]) and len(list(set(arr))) == len(arr)
        elif module_name == 'mergesort':
            arr = tinput[0]
            return isinstance(arr, list) and all([isinstance(i, int) for i in arr])
        elif module_name == 'bucketsort':
            arr, k = tuple(tinput)
            return all(isinstance(x, int) and 0 <= x < k for x in arr)
        elif module_name == 'shunting_yard':
            tokens = tinput[0]
            return all(isinstance(token, int) or token in '+-*/' for token in tokens)
        elif module_name == 'hanoi':
            height, start, end = tuple(tinput)
            return height >= 0 and start in (1, 2, 3) and end in (1, 2, 3)
        elif module_name == 'gcd':
            a, b = tuple(tinput)
            return isinstance(a, int) and isinstance(b, int) and a >= 0 and b >= 0
        elif module_name == 'to_base':
            num, b = tuple(tinput)
            return num > 0 and 2 <= b <= 36
        elif module_name == 'possible_change':
            #coins: A list of positive ints representing coin denominations
            #total: An int value to make change for
            coins, total = tuple(tinput)
            return isinstance(coins, list) and all([isinstance(x, int) and x > 0 for x in coins])
        elif module_name == 'bitcount':
            n = tinput[0]
            return n >= 0
        elif module_name == 'wrap':
            #text: The starting text.
            #cols: The target column width, i.e. the maximum length of any single line after wrapping.
            text, cols = tuple(tinput)
            return cols > 0
    except KeyboardInterrupt:
        raise KeyboardInterrupt
    except:
        return False

def gen(correct, buggy, tests, module_name):
    signal.signal(signal.SIGALRM, handler)
    #print(correct(*base))
    #print(buggy(*base))
    passing = list()
    for test in tests:
        base = test[0]
        if not isinstance(base, list):
            base = [base]
        for i in range(TRY):
            #if i % 10 == 0:
                #print(base, i)
            neighbours = get_neighbours(base, 2, 0.001)
            for neighbour in neighbours:
                try:
                    signal.alarm(TIMELIMIT)
                    correct_result = correct(*neighbour)
                    signal.alarm(TIMELIMIT)
                    buggy_result = buggy(*neighbour)
                    if correct_result == buggy_result:
                        if neighbour not in passing and is_valid_input(module_name, neighbour):
                            #print([neighbour, correct_result])
                            passing.append([neighbour, correct_result])
                        #return neighbour
                except KeyboardInterrupt:
                    raise KeyboardInterrupt
                except Exception as e:
                    pass
            base = random.choice(neighbours)
    return passing

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
    print(module_name)
    result = gen(correct_func, buggy_func, tests, module_name)
    print(len(result))
    with open("passing_{}.json".format(module_name), 'a') as f:
        for item in result:
            f.write(str(item) + '\n')
    #if result:
    #    print(module_name, result)

if __name__ == "__main__":
    for target in TARGETS:
        run(target)
    #module_name = sys.argv[1]
