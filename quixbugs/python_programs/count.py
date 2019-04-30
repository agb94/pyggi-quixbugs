import sys
import json
import importlib
import signal
import os
import types
from test import run

EXCLUDED = ['hanoi', 'levenshtein', 'knapsack', 'sqrt']

if __name__ == "__main__":
    print("subject,passing,timeout,failing")
    for test in os.listdir('../json_testcases'):
        module_name = os.path.splitext(test)[0]
        if module_name in EXCLUDED:
            continue
        test_file = "../json_testcases/{}.json".format(module_name)
        passing, timeout, failing = run(module_name, test_file)
        print(','.join(list(map(str, [module_name, passing, timeout, failing]))))
