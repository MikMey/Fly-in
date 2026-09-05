import sys
from typing import Optional

from src import cache_input, cost_calc, Data, Hub, Drone, Connection, send_drones


def main(argv: Optional[list[str]] = None) -> None:

	args = sys.argv[1:] if argv is None else argv
	if len(args) > 1 or len(args) == 0:
		sys.exit("Please parse file as first and only argument")

	objects: Data = cache_input(args[0])
	objects = cost_calc(objects)
	# for value in objects.values():
	# 		for i in value:
	# 			if type(i) == Hub:
	# 				print(i.name, i.max_cost)
	turns = send_drones(objects)
	print(f"Total turns: {turns}")
	

if __name__ == "__main__":
	main()