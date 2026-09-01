import sys
from typing import Optional

from src import validate, cache_input


def main(argv: Optional[list[str]] = None):

	args = sys.argv[1:] if argv is None else argv
	if len(args) > 1 or len(args) == 0:
		sys.exit("Please parse file as first and only argument")

	cache_input(args[0])
	

if __name__ == "__main__":
	main()