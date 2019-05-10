import os
import random
import json
import argparse
import copy
import re
from pyggi.base import Patch, StatusCode
from pyggi.line import LineReplacement, LineInsertion, LineDeletion
from pyggi.tree import StmtReplacement, StmtInsertion, StmtDeletion
from pyggi.utils import get_file_extension
from quixbugsjava import MyTreeProgram, MyLineProgram, QUIXBUGS_DIR, JAVA_DIR, JAVA_XML_DIR

PATCH = "StmtReplacement({'target': ('SIEVE.java.xml', 16), 'ingredient': ('SIEVE.java.xml', 15)}) | StmtReplacement({'target': ('SIEVE.java.xml', 11), 'ingredient': ('SIEVE.java.xml', 3)})"
"""
def run(mode, target, epoch, maxiter):
    target_path = os.path.join(JAVA_DIR, target + '.java')
    print("------------------- Target -------------------")
    print(target_path)

    if mode == 'line':
        config = {
            'target_files': [target.upper() + '.java'],
            'test_command': None
        }
        program = MyLineProgram(JAVA_DIR, config=config)
        operators = [LineReplacement, LineInsertion, LineDeletion]
    elif mode == 'tree':
        config = {
            'target_files': [target.upper() + '.java.xml'],
            'test_command': None
        }
        program = MyTreeProgram(JAVA_XML_DIR, config=config)
        operators = [StmtReplacement, StmtInsertion, StmtDeletion]
    program.algo = target
    program.tests = []
    with open(os.path.join(JSON_DIR, "{}.json".format(target)), 'r') as f:
        for line in f:
            py_testcase = json.loads(line)
            test_in, test_out = py_testcase
            if not isinstance(test_in, list):
                test_in = [test_in]
            program.tests.append((test_in, test_out))

    patch = Patch(program)
    #print(program.run())
    print(program.evaluate_patch(patch))

    class MyLocalSearch(LocalSearch):
        def get_neighbour(self, patch):
            temp_patch = patch.clone()
            if len(temp_patch) > 0 and random.random() < 0.1:
                temp_patch.remove(random.randrange(0, len(temp_patch)))
            else:
                edit_operator = random.choice(operators)
                temp_patch.add(edit_operator.create(program, method="weighted"))
            return temp_patch

        def is_better_than_the_best(self, fitness, best_fitness):
            return best_fitness is None or fitness < best_fitness

        def stopping_criterion(self, iter, fitness):
            return fitness == 0

    local_search = MyLocalSearch(program)
    result = local_search.run(warmup_reps=1, epoch=epoch, max_iter=maxiter, timeout=10)
    for epoch in range(len(result)):
        if result[epoch]["BestPatch"] is not None:
            result[epoch]["diff"] = program.diff(result[epoch]["BestPatch"])
        result[epoch]["BestPatch"] = str(result[epoch]["BestPatch"])
    with open("./logs-java/{}_{}_{}".format(program.timestamp, mode, target), 'w') as f:
        f.write(json.dumps(result))
    program.remove_tmp_variant()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', type=str, default='line')
    parser.add_argument('--targets', type=str, default='TARGETS')
    parser.add_argument('--epoch', type=int, default=20)
    parser.add_argument('--maxiter', type=int, default=500)
    args = parser.parse_args()
    TARGETS = list(map(lambda s: s.strip(), open(args.targets, 'r').readlines()))
    for target in TARGETS:
        run(args.mode, target, args.epoch, args.maxiter)
"""

if __name__ == "__main__":
    edits = PATCH.split('|')
