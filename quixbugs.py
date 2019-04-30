import os
import random
import json
import argparse
from pyggi.base import Patch
from pyggi.line import LineProgram
from pyggi.line import LineReplacement, LineInsertion, LineDeletion
from pyggi.tree import TreeProgram
from pyggi.tree import StmtReplacement, StmtInsertion, StmtDeletion
from pyggi.algorithms import LocalSearch

QUIXBUGS_DIR = os.path.abspath("./quixbugs")
PYTHON_DIR = os.path.join(QUIXBUGS_DIR, "python_programs")
JSON_DIR = os.path.join(QUIXBUGS_DIR, "json_testcases")
TARGETS = list(map(lambda s: s.strip(), open('TARGETS', 'r').readlines()))

def run(mode, target, epoch, maxiter):
	target_path = os.path.join(PYTHON_DIR, target + '.py')
	test_path = os.path.join(JSON_DIR, target + '.json')
	print("------------------- Target -------------------")
	print(target_path)
	print("-------------------- Test --------------------")
	print(test_path)
	print("----------------------------------------------")

	config = {
		'target_files': [target + '.py'],
		'test_command': "python test.py {} {}".format(target, test_path)
	}
	if mode == 'line':
		program = LineProgram(PYTHON_DIR, config=config)
		operators = [LineReplacement, LineInsertion, LineDeletion]
	elif mode == 'tree':
		program = TreeProgram(PYTHON_DIR, config=config)
		operators = [StmtReplacement, StmtInsertion, StmtDeletion]

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
	for mode in ['line', 'tree']:
		for target in TARGETS:
			run(mode, target, args.epoch, args.maxiter)
