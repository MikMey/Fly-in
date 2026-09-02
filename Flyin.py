import sys
from typing import Optional

from src import cache_input, cost_calc, Data, Hub, Drone, Connection


def main(argv: Optional[list[str]] = None):

	args = sys.argv[1:] if argv is None else argv
	if len(args) > 1 or len(args) == 0:
		sys.exit("Please parse file as first and only argument")

	objects: Data = cache_input(args[0])
	objects = cost_calc(objects)
	for value in objects.values():
			for i in value:
				if type(i) == Hub:
					print(i.name, i.max_cost)
				elif type(i) == Connection:
					print(f"{i.start}-{i.end} {i.max_cost}")
	

if __name__ == "__main__":
	main()