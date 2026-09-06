import sys
from time import sleep
from typing import Any

from colour import Color

from .models import Data, Hub, Connection, Drone

def _find_connection(hub: Hub, moving: int) -> Hub | None:
	targets: list[Hub] = []
	for connection in hub.connections:
		if connection.used >= connection.max_link_capacity:
			continue
		targets.append(next(target for target in connection.hubs if target.name != hub.name))
	for target in targets.copy():
		if len(target.drones) >= target.max_drones and target.group != 'end_hub':
			targets.remove(target)
		elif target.max_cost + 1 > hub.max_cost + moving:
			targets.remove(target)
	if not targets or not targets[0]:
		return None
	targets.sort(key=lambda target: target.max_cost)
	cost = targets[0].max_cost
	for item in targets.copy():
		if item.max_cost > cost:
			targets.remove(item)
	target = targets[0]
	for item in targets:
		if item.zone == "priority":
			target = item
			break
	con = next(con for con in target.connections if hub.name in con.link)
	con.used += 1
	return target
	

def _show_move(target: Hub, drone: str, restricted: bool = False) -> None:
	r = int(target.color.red * 255)
	g = int(target.color.green * 255)
	b = int(target.color.blue * 255)
	print(f"\033[38;2;{r};{g};{b}m{drone}-{target.name}\033[0m", end="")
	if restricted:
		print("[restricted]", end=" ")
	else:
		print("", end=" ")


def send_drones(objects: Data) -> int:
	# for i in objects[Hub]:
	# 	print(i.max_cost)
	turn_counter = 0
	moving: int = objects[Drone][0].number

	"""
	put all drones on start hub from D1 to Dx
	"""
	hub = next(hub for hub in objects[Hub] if hub.group == 'start_hub')
	for i in range(objects[Drone][0].number):
		hub.drones[f"D{i}"] = 0

	"""
	while number of drones > drones at end hub
	"""
	while objects[Drone][0].number > len(objects[Hub][0].drones):
		# sleep(0.1)
		busy: list[str] = []
		for con in objects[Connection]:
			con.used = 0
		turn_counter += 1
		print(f"Turn: {turn_counter} - ", end="")
		for hub in objects[Hub]:
			if hub.group == 'end_hub':
				continue
			if len(hub.drones) == 0:
				continue
			for drone, counter in list(hub.drones.items()):
				if drone in busy:
					continue
				busy.append(drone)
				if counter > 0:
					hub.drones[drone] = 0
					continue
				target = _find_connection(hub, moving)
				if target is None:
					continue
				hub.drones.__delitem__(drone)
				target.drones[drone] = 0
				if target.zone == 'restricted':
					target.drones[drone] = 1
					_show_move(target, drone, True)
				else:
					_show_move(target, drone)
				if target.group == 'end_hub':
					moving -= 1
		print(f"", end="\n")
	if turn_counter == 0:
		sys.exit("Graph doesnt connect start and end")

	return turn_counter

