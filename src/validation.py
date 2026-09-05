from typing import Any, cast
import sys

import re
from pydantic import BaseModel, Field, ValidationError, model_validator
from colour import Color

from .models import Drone, Connection, Hub, Data

drones_pattern = re.compile(
	r"^(?P<group>\w+):\s+(?P<number>\w+)$"
)
hub_pattern = re.compile(
    r"^(?P<group>\w+):\s+(?P<name>\w+)\s+(?P<x>[^ ]+)\s+(?P<y>[^ ]+)" \
    r"(?:\s+\[(?P<metadata>[^\]]+)\])?$"
)
connection_pattern = re.compile(
	r"^(?P<group>\w+):\s+(?P<start>\w+)-(?P<end>\w+)" \
	r"(?:\s+\[(?P<metadata>[^\]]+)\])?$"
)


GROUPS: list = ["nb_drones", "start_hub", "end_hub", "hub", "connection"]
PATTERNS: list = [drones_pattern, hub_pattern, connection_pattern]
MATCHES: dict[str, type[Drone] | type[Hub] | type[Connection]] = {
	'nb_drones': Drone,
	'start_hub': Hub,
	'end_hub': Hub,
	'hub': Hub,
	'connection': Connection
}

def _create_obj(class_type: type[BaseModel], objects: Data, matched: re.Match)\
	-> Data:
	checked = cast(Drone | Hub | Connection, class_type.model_validate(matched.groupdict()))
	if type(checked) == Hub:
		if any(checked.name == i.name for i in objects[type(checked)] if type(i) == Hub):
			sys.exit("Duplicate name")
	elif type(checked) == Connection:
		if any(checked.link == i.link for i in objects[type(checked)] if type(i) == Connection):
			sys.exit(f"Duplicate route with \"{checked.start}-{checked.end}\"")
	objects[type(checked)].append(checked)
	return(objects)

def cache_input(filepath: str) -> Data:
	objects: Data = {
		Drone: [],
		Hub: [],
		Connection: []
	}
	try:
		with open(file=filepath, mode='r') as file:
			for i, line  in enumerate(file):
				if "#" in line or ":" not in line:
					continue
				if not any(elem in line for elem in GROUPS):
					sys.exit(f"Provided file contains bad information in line {i + 1}:\n\"{line}\"")
				line = line.strip().lower()
				for pattern in PATTERNS:
					matched = re.match(pattern, line)
					if matched:
						break
				if not matched:
					sys.exit(f"Provided file contains bad information in line {i + 1}:\n\"{line}\"")
				try:
					group = matched.groupdict()['group']
					objects = _create_obj(MATCHES[group], objects, matched)
				except ValidationError as err:
					sys.exit(f"Error in validation:\n{err}")
				except Exception as err:
					sys.exit(f"Error:\n{err}")
	except FileNotFoundError as err:
		sys.exit(f"File \"{filepath}\" doesnt exist:\n{err}")
	except Exception as err:
		sys.exit(f"Something went wrong:\n{err}")
	objects = verify(objects)
	
	return(objects)

def _clear_connections(objects: Data) -> Data:
	for con in objects[Connection]:
		if not any(con.start == hub.name for hub in objects[Hub]) or\
			not any(con.end == hub.name for hub in objects[Hub]):
			objects[Connection].remove(con)
	return objects

def _clear_hubs(objects: Data) -> Data:
	i = 0
	remove = True
	while remove:
		remove = False
		for hub in objects[Hub]:
			if hub.group == 'hub':
				for con in objects[Connection]:
					if hub.name == con.start or hub.name == con.end:
						i += 1
				if i <= 1 or hub.zone == 'blocked':
					objects[Hub].remove(hub)
					objects = _clear_connections(objects)
					remove = True
			i = 0
	return objects

def _attach_objects(objects: Data) -> Data:
	for hub in objects[Hub]:
		for con in objects[Connection]:
			if hub.name == con.start or hub.name == con.end:
				hub.connections.append(con)
				con.hubs.append(hub)
	return objects


def verify(objects: Data) -> Data:
	if not any('start_hub' == hub.group for hub in objects[Hub]) or\
		not any('end_hub' == hub.group for hub in objects[Hub]):
		sys.exit(f"Start and/or exit dont exit")
	for con in objects[Connection]:
		if any(con.start == hub.name for hub in objects[Hub]) and\
			any(con.end == hub.name for hub in objects[Hub]):
			break
		else:
			sys.exit(f"Connection \"{con.start}-{con.end}\"contains invalid nodes")
	objects = _clear_hubs(objects)
	objects = _attach_objects(objects)

	return objects
