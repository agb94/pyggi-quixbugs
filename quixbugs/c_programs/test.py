import sys
import json
import importlib
import signal

TIMELIMIT = 10

class TIMEOUT(Exception):
    pass

def handler(signum, frame):
    raise TIMEOUT

module_name = sys.argv[1]
mod = importlib.import_module(module_name)
func = mod.__dict__[module_name]
#test_file = "../json_testcases/{}.json".format(module_name)
test_file = sys.argv[2]
tests = []
with open(test_file, 'r') as f:
    for l in f.readlines():
        if l.strip():
            tests.append(eval(l))

signal.signal(signal.SIGALRM, handler)

passing = 0
failing = 0
timeout = 0
for test in tests:
    try:
        signal.alarm(TIMELIMIT)
        result = func(*test[0])
        if test[1] == result:
            passing += 1
        else:
            failing += 1
    except TIMEOUT:
        timeout += 1
    except:
        failing += 1

print(timeout + failing)
