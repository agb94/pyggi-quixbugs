import os
import sys
import importlib
import operator
import random
import argparse
from pyggi.base import Patch
from pyggi.tree import TreeProgram
from pyggi.tree import StmtDeletion, StmtInsertion, StmtReplacement
from pyggi.line import LineProgram
from pyggi.line import LineDeletion, LineInsertion, LineReplacement

ITERS = 500
QUIXBUGS_DIR = os.path.abspath(".")
PYTHON_DIR = os.path.join(QUIXBUGS_DIR, "python_programs")
tests = {}
patches = []

class MyTreeProgram(TreeProgram):
    def compute_fitness(self, elapsed_time, stdout, stderr):
        failing_tests = []
        for test in list(filter(lambda s: s.strip(), stdout.split('\n'))):
            if test not in failing_tests:
                failing_tests.append(test)
        return failing_tests

class MyLineProgram(LineProgram):
    def compute_fitness(self, elapsed_time, stdout, stderr):
        failing_tests = []
        for test in list(filter(lambda s: s.strip(), stdout.split('\n'))):
            if test not in failing_tests:
                failing_tests.append(test)
        return failing_tests


def run(module_name):
    config = {
        'target_files': [module_name + '.py'],
        'test_command': "python test_verbose.py {} {}".format(module_name,
            os.path.join(QUIXBUGS_DIR, "passings/passing_{}.json".format(module_name)))
    }
    
    setups = [
            ( MyTreeProgram, [StmtReplacement, StmtInsertion, StmtDeletion] ),
            ( MyLineProgram, [LineReplacement, LineInsertion, LineDeletion] )
    ]
    for Program, operators in setups:
        program = Program(PYTHON_DIR, config=config)
        for i in range(ITERS):
            patch = Patch(program)
            patch.add(random.choice(operators).create(program))
            status, failing_tests = program.evaluate_patch(patch)
            if str(patch) not in patches:
                patches.append(str(patch))
            if failing_tests is not None:
                for test in failing_tests:
                    if not test in tests:
                        tests[test] = []
                    if not str(patch) in tests[test]:
                        tests[test].append(str(patch))
        program.remove_tmp_variant()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('module_name', type=str, default='gcd')
    parser.add_argument('--correct', action='store_true')
    parser.add_argument('--iters', type=int, default=500)
    args = parser.parse_args()
    if args.correct:
        PYTHON_DIR = os.path.join(QUIXBUGS_DIR, "correct_python_programs")
    ITERS = args.iters

    module_name = args.module_name
    run(module_name)
    patterns = {}
    for test in tests:
        pattern = ''.join([ str(int(patch not in tests[test])) for patch in patches ])
        if not pattern in patterns:
            patterns[pattern] = []
        patterns[pattern].append(test)
    
    with open("passings/passing_{}{}.txt".format(module_name, "_correct" if args.correct else ""), "w") as f:
        for pattern, tests in list(reversed(sorted(patterns.items(), key=lambda t: t[0].count('0')))):
            f.write(str(pattern.count('0')/len(pattern)) + '\n')
            for test in tests:
                f.write(test + '\n')
            f.write('\n')

    with open("passings/passing_{}_patches{}.txt".format(module_name, "_correct" if args.correct else ""), "w") as f:
        for patch in patches:
            f.write(patch + '\n')
