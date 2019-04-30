import sys
import json
import importlib
import signal
import types

TIMELIMIT = 10

class TIMEOUT(Exception):
    pass

def handler(signum, frame):
    raise TIMEOUT

def run(module_name, test_file):
    mod = importlib.import_module(module_name)
    func = mod.__dict__[module_name]
    tests = []
    with open(test_file, 'r') as f:
        for l in f.readlines():
            if l.strip():
                tests.append(eval(l.replace('true', 'True').replace('false', 'False')))

    signal.signal(signal.SIGALRM, handler)

    passing = 0
    failing = 0
    timeout = 0
    for test in tests:
        try:
            signal.alarm(TIMELIMIT)
            if isinstance(test[0], list):
                result = func(*test[0])
            else:
                result = func(test[0])
            if isinstance(result, types.GeneratorType):
                result = list(result)
            if test[1] == result:
                passing += 1
            else:
                failing += 1
        except TIMEOUT:
            timeout += 1
        except:
            failing += 1
    return passing, timeout, failing

if __name__ == "__main__":
    module_name = sys.argv[1]
    test_file = sys.argv[2]
    passing, timeout, failing = run(module_name, test_file)
    print(timeout + failing)
