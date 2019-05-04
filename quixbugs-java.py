import os
import random
import json
import argparse
import copy
from pyggi.base import Patch, StatusCode
from pyggi.line import LineProgram
from pyggi.line import LineReplacement, LineInsertion, LineDeletion
from pyggi.tree import TreeProgram
from pyggi.tree import StmtReplacement, StmtInsertion, StmtDeletion
from pyggi.algorithms import LocalSearch

QUIXBUGS_DIR = os.path.abspath("./quixbugs")
JAVA_DIR = os.path.join(QUIXBUGS_DIR, "java_programs")
JSON_DIR = os.path.join(QUIXBUGS_DIR, "json_testcases")
TARGETS = list(map(lambda s: s.strip(), open('TARGETS', 'r').readlines()))
COMPILE_COMMAND = "javac LIS.java -d ."
TEST_COMMAND = "java -cp gson-2.8.2.jar:. JavaDeserialization {} {}"

class MyLineProgram(LineProgram):
    def run(self, timeout=10):
        try_compile = self.exec_cmd(COMPILE_COMMAND.format(self.algo.upper()), timeout)
        if try_compile.stderr:
            result = self.__class__.Result(
                            status_code=StatusCode.PARSE_ERROR,
                            elapsed_time=try_compile.elapsed_time,
                            stdout=try_compile.stdout,
                            stderr=try_compile.stderr)
        else:
            failing = 0
            elapsed_time = 0
            for test in self.tests:
                test_in, test_out = test
                algo_input = ['"'+json.dumps(arg)+'"' for arg in copy.deepcopy(test_in)]
                try_test = self.exec_cmd(TEST_COMMAND.format(self.algo, ' '.join(algo_input)), timeout)
                #print(TEST_COMMAND.format(self.algo, ' '.join(algo_input)))
                #print(try_test.stdout.strip(), str(test_out))
                if not try_test.stdout.rstrip() == str(test_out):
                    failing += 1
                elapsed_time += try_test.elapsed_time
            result = self.__class__.Result(
                status_code=StatusCode.NORMAL,
                elapsed_time=elapsed_time,
                stdout=str(failing),
                stderr='')
        return result

class MyTreeProgram(TreeProgram):
    pass

def run(mode, target, epoch, maxiter):
    target_path = os.path.join(JAVA_DIR, target + '.py')
    test_path = os.path.join(JSON_DIR, target + '.json')
    print("------------------- Target -------------------")
    print(target_path)
    print("-------------------- Test --------------------")
    print(test_path)
    print("----------------------------------------------")

    config = {
        'target_files': [target.upper() + '.java'],
        'test_command': None
    }
    if mode == 'line':
        program = MyLineProgram(JAVA_DIR, config=config)
        operators = [LineReplacement, LineInsertion, LineDeletion]
    elif mode == 'tree':
        program = MyTreeProgram(JAVA_DIR, config=config)
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

    print(program.run())
    patch = Patch(program)
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
    with open("./logs/{}_{}_{}".format(program.timestamp, mode, target), 'w') as f:
        f.write(json.dumps(result))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    #parser.add_argument('--mode', type=str, default='line')
    #parser.add_argument('--target', type=str, default='gcd')
    parser.add_argument('--epoch', type=int, default=30)
    parser.add_argument('--maxiter', type=int, default=100)
    args = parser.parse_args()
    run('line', 'lis', args.epoch, args.maxiter)
    """
    for mode in ['line', 'tree']:
        for target in TARGETS:
            run(mode, target, args.epoch, args.maxiter)
    """
