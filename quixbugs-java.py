import os
import random
import json
import argparse
import copy
import re
from pyggi.base import Patch, StatusCode
from pyggi.line import LineProgram
from pyggi.line import LineReplacement, LineInsertion, LineDeletion
from pyggi.tree import TreeProgram, AstorEngine, XmlEngine
from pyggi.tree import StmtReplacement, StmtInsertion, StmtDeletion
from pyggi.algorithms import LocalSearch
from pyggi.utils import get_file_extension

QUIXBUGS_DIR = os.path.abspath("./quixbugs")
JAVA_DIR = os.path.join(QUIXBUGS_DIR, "java_programs")
JAVA_XML_DIR = os.path.join(QUIXBUGS_DIR, "java_xml_programs")
JSON_DIR = os.path.join(QUIXBUGS_DIR, "json_testcases")
TARGETS = list(map(lambda s: s.strip(), open('TARGETS', 'r').readlines()))
COMPILE_COMMAND = "javac {}.java -d ."
TEST_COMMAND = "java -cp gson-2.8.2.jar:. JavaDeserialization {} {}"

STMT_TAGS = ['if', 'then', 'else', 'elseif', 'while', 'for', 'do',
    'break', 'continue', 'return', 'switch', 'case', 'default', 'block',
    'label', 'goto', 'empty_stmt', 'foreach', 'fixed', 'using', 'unsafe', 'assert'
]

class MyXmlEngine(XmlEngine):
    @classmethod
    def get_contents(cls, file_path):
        tree = XmlEngine.get_contents(file_path)
        cls.remove_tags(tree, exception=STMT_TAGS)
        cls.rotate_newlines(tree)
        print(cls.tree_to_string(tree))
        print('------------------------------------')
        return tree

    @classmethod
    def remove_tags(cls, element, exception=[]):
        last = None
        marked = []
        buff = 0
        for i, child in enumerate(element):
            cls.remove_tags(child, exception=exception)
            if child.tag not in exception:
                marked.append(child)
                if child.text:
                    if last is not None:
                        last.tail = last.tail or ''
                        last.tail += child.text
                    else:
                        element.text = element.text or ''
                        element.text += child.text
                if len(child) > 0:
                    for sub_child in reversed(child):
                        element.insert(i+1, sub_child)
                    last = child[-1]
                if child.tail:
                    if last is not None:
                        last.tail = last.tail or ''
                        last.tail += child.tail
                    else:
                        element.text = element.text or ''
                        element.text += child.tail
            else:
                last = child
        for child in marked:
            element.remove(child)

    @classmethod
    def rewrite_tags(cls, element, tags, new_tag):
        if element.tag in tags:
            element.tag = new_tag
        for child in element:
            cls.rewrite_tags(child, tags, new_tag)

    @classmethod
    def rotate_newlines(cls, element):
        if element.tail:
            match = re.match("(\n\s*)", element.tail)
            if match:
                element.tail = element.tail[len(match.group(1)):]
                if len(element) > 0:
                    element[-1].tail = element[-1].tail or ''
                    element[-1].tail += match.group(1)
                else:
                    element.text = element.text or ''
                    element.text += match.group(1)
        for child in element:
            cls.rotate_newlines(child)

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
                if try_test.stdout is None or try_test.stdout.rstrip() != str(test_out):
                    failing += 1
                elapsed_time += try_test.elapsed_time if try_test.elapsed_time else timeout
            result = self.__class__.Result(
                status_code=StatusCode.NORMAL,
                elapsed_time=elapsed_time,
                stdout=str(failing),
                stderr='')
        return result

class MyTreeProgram(TreeProgram):
    @classmethod
    def get_engine(cls, file_name):
        extension = get_file_extension(file_name)
        if extension in ['.py']:
            return AstorEngine
        elif extension in ['.xml']:
            return MyXmlEngine
        else:
            raise Exception('{} file is not supported'.format(extension))

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
                if try_test.stdout is None or try_test.stdout.rstrip() != str(test_out):
                    failing += 1
                elapsed_time += try_test.elapsed_time if try_test.elapsed_time else timeout
            result = self.__class__.Result(
                status_code=StatusCode.NORMAL,
                elapsed_time=elapsed_time,
                stdout=str(failing),
                stderr='')
        return result

def run(mode, target, epoch, maxiter):
    target_path = os.path.join(JAVA_DIR, target + '.java')
    test_path = os.path.join(JSON_DIR, target + '.json')
    print("------------------- Target -------------------")
    print(target_path)
    print("-------------------- Test --------------------")
    print(test_path)
    print("----------------------------------------------")


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
