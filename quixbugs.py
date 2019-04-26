import os
import random
import argparse
from pyggi.base import Patch
from pyggi.line import LineProgram
from pyggi.line import LineReplacement, LineInsertion, LineDeletion
from pyggi.tree import TreeProgram
from pyggi.tree import StmtReplacement, StmtInsertion, StmtDeletion
from pyggi.algorithms import LocalSearch

QUIXBUGS_DIR = "/Users/gabin/Workspace/pyggi-quixbugs/quixbugs"
PYTHON_DIR = os.path.join(QUIXBUGS_DIR, "python_programs")
JSON_DIR = os.path.join(QUIXBUGS_DIR, "json_testcases")

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('--mode', type=str, default='line')
	parser.add_argument('--target', type=str, default='gcd')
	parser.add_argument('--epoch', type=int, default=1)
	parser.add_argument('--maxiter', type=int, default=100)
	args = parser.parse_args()

	target = os.path.join(PYTHON_DIR, args.target + '.py')
	test = os.path.join(JSON_DIR, args.target + '.json')
	print("------------------- Target -------------------")
	print(target)
	print("-------------------- Test --------------------")
	print(test)
	print("----------------------------------------------")

	config = {
		'target_files': [args.target + '.py'],
		'test_command': "python test.py {} {}".format(args.target, test)
	}
	if args.mode == 'line':
		program = LineProgram(PYTHON_DIR, config=config)
		operators = [LineReplacement, LineInsertion, LineDeletion]
	elif args.mode == 'tree':
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
			return fitness < best_fitness

		def stopping_criterion(self, iter, fitness):
			return fitness == 0

	local_search = MyLocalSearch(program)
	result = local_search.run(warmup_reps=1, epoch=args.epoch, max_iter=args.maxiter, timeout=10)
	for epoch in result:
		print ("Epoch #{}".format(epoch))
		for key in result[epoch]:
			print ("- {}: {}".format(key, result[epoch][key]))
		if result[epoch]["BestPatch"] is not None:
			print(program.diff(result[epoch]["BestPatch"]))
