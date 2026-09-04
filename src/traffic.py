import sys
from time import sleep
from typing import Any

from .models import Data, Hub, Connection, Drone

def _find_connection(hub: Hub, moving: int) -> Hub:
	targets: list[Hub] = []
	for connection in hub.connections:
		if connection.used >= connection.max_link_capacity:
			continue
		targets.append(next(target for target in connection.hubs if target.name != hub.name))
	for target in targets.copy():
		if len(target.drones) >= target.max_drones:
			targets.remove(target)
	if not targets or not targets[0]:
		return None
	targets.sort(key=lambda target: target.max_cost)
	return targets[0]
	

def _show_move(target: Hub, drone: str, restricted: bool = False) -> None:
	print(f"{drone}-{target.name}", end="")
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
		# sleep(1)
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
				if counter > 0:
					hub.drones[drone] = 0
					continue
				target: Hub = _find_connection(hub, moving)
				if target == None:
					continue
				#TODO hubs called after current, dont know if drone was sent here this turn
				#TODO cost implementation to _find_connection
				#TODO drones dont reach end
				hub.drones.__delitem__(drone)
				target.drones[drone] = 0
				if target.zone == 'restricted':
					target.drones[drone] = 1
					_show_move(target, drone, True)
				else:
					_show_move(target, drone)
				if target.group == 'end_zone':
					moving -= 1
		if turn_counter > 50:
			break
		print(f"\n{moving}", end="\n")

	return turn_counter

