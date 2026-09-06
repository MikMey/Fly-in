import sys
from typing import Any

from .models import Data, Hub, Connection, Drone


def cost_calc(objects: Data) -> Data:
	#minor bug, connection cost always from smaller node to greater node
	stack: list[Hub] = []
	i = 0
	stack.append(next(elem for elem in objects[Hub] if elem.group =='end_hub'))
	stack[i].max_cost = 0
	try:
		while i < (len(objects[Hub]) - 1):
			for con in stack[i].connections:
				# if con.max_cost == -1 and (con.end == stack[i].name or con.start == stack[i].name):
				# 	con.max_cost = stack[i].max_cost + 1
				if con.start == stack[i].name:
					check = next(elem for elem in objects[Hub] if elem.name == con.end)
				else:
					check = next(elem for elem in objects[Hub] if elem.name == con.start)
				if check.max_cost == -1:
					check.max_cost = next(hub.max_cost for hub in con.hubs if hub.name != check.name) + 1
					if check.zone == 'restricted':
						check.max_cost += 1
					stack.append(check)
			i += 1
	except IndexError:
		sys.exit("No connection from Start to End")
	except Exception as err:
		sys.exit(f"Error:\n{err}")
	objects[Hub].sort(key=lambda hub: hub.max_cost)
	return objects
