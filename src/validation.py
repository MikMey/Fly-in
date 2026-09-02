from typing import Any
import sys

import re
from pydantic import BaseModel, Field, ValidationError, model_validator
from colour import Color



class Drone(BaseModel):
	group: str = "nb_drones"
	number: int = Field(..., ge=1, le=999999)

ZONES: list = ['normal', 'blocked', 'priority', 'restricted']

class Hub(BaseModel):
	group: str = Field(..., min_length=3, max_length=9)
	name: str = Field(..., min_length=1)
	x: int = Field(..., ge=0, le=9999)
	y: int = Field(..., ge=0, le=9999)
	zone: str = Field(default="normal")
	color: Any = Field(default=None)
	max_drones: int = Field(default=1, ge=0, le=99999)

	@model_validator(mode="before")
	def prep(self: dict[str, str | Any]):
		if self['metadata']:
			self['metadata'] = self['metadata'].split(' ')
			for i in self['metadata']:
				if not re.match(metadata_pattern, i):
					sys.exit(f"Invalid Metadata format:\n\"{i}\"")
				metadata = i.split('=', 1)
				self[metadata[0]] = metadata[1]
			self.pop('metadata')
		if self['color']:
			try:
				self['color'] = Color(self['color'])
			except Exception as err:
				sys.exit(f"Color Error in \"{self['name']}\":\n{err}")
		return self

	@model_validator(mode='after')
	def validate(self):
		if self.zone not in ZONES:
			sys.exit(f"Invalid hub zone \"{self.zone}\" at \"{self.name}\"")
		return self

class Connection(BaseModel):
	group: str = "connection"
	start: str = Field(..., min_length=1)
	end: str = Field(..., min_length=1)
	max_link_capacity: int = Field(default=1, ge=0, le=99999)

	@model_validator(mode="before")
	def prep(self: dict[str, str | Any]):
		if self['metadata']:
			self['metadata'] = self['metadata'].split(' ')
			for i in self['metadata']:
				if not re.match(metadata_pattern, i):
					sys.exit(f"Invalid Metadata format:\n\"{i}\"")
				metadata = i.split('=', 1)
				self[metadata[0]] = metadata[1]
			self.pop('metadata')
		return self

	@model_validator(mode='after')
	def validate(self):
		if self.start == self.end:
			sys.exit(f"Connection \"{self.start}-{self.end}\" ends in itself")
		return self


drones_pattern = re.compile(
	r"^(?P<group>\w+):\s+(?P<number>\w+)$"
)
hub_pattern = re.compile(
    r"^(?P<group>\w+):\s+(?P<name>\w+)\s+(?P<x>\d+)\s+(?P<y>\d+)" \
    r"(?:\s+\[(?P<metadata>[^\]]+)\])?$"
)
connection_pattern = re.compile(
	r"^(?P<group>\w+):\s+(?P<start>\w+)-(?P<end>\w+)" \
	r"(?:\s+\[(?P<metadata>[^\]]+)\])?$"
)
metadata_pattern = re.compile(
	r"^(\w+)=([^\s]+)$"
)

GROUPS: list = ["nb_drones", "start_hub", "end_hub", "hub", "connection"]
PATTERNS: list = [drones_pattern, hub_pattern, connection_pattern]
MATCHES: dict[str, BaseModel] = {
	'nb_drones': Drone,
	'start_hub': Hub,
	'end_hub': Hub,
	'hub': Hub,
	'connection': Connection
}

def _create_obj(class_type: BaseModel, objects: dict[Drone|Hub|Connection, list[Drone|Hub|Connection]], matched: re.Match)\
	-> dict[Drone|Hub|Connection, list[Drone|Hub|Connection]]:
	checked: Drone|Hub|Connection = class_type.model_validate(matched.groupdict())
	if type(checked) == Hub:
		if any(checked.name == i.name for i in objects[type(checked)] if type(i) == Hub):
			sys.exit("Duplicate name")
	elif type(checked) == Connection:
		if any(checked.start == i.start for i in objects[type(checked)] if type(i) == Connection)\
			and any(checked.end == i.end for i in objects[type(checked)] if type(i) == Connection):
			sys.exit("Duplicate route")
	objects[type(checked)].append(checked)
	return(objects)

def cache_input(filepath: str) -> dict[Drone|Hub|Connection, list[Drone|Hub|Connection]]:
	objects: dict[Drone|Hub|Connection, list[Drone|Hub|Connection]] = {
		Drone: [],
		Hub: [],
		Connection: []
	}
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
	objects = verify(objects)
	for value in objects.values():
		for i in value:
			print(i)
	return(objects)

def _clear_connections(objects: dict[Drone|Hub|Connection, list[Drone|Hub|Connection]]) -> dict[Drone|Hub|Connection, list[Drone|Hub|Connection]]:
	for con in objects[Connection]:
		if not any(con.start == hub.name for hub in objects[Hub]) or\
			not any(con.end == hub.name for hub in objects[Hub]):
			objects[Connection].remove(con)
	return objects

def _clear_hubs(objects: dict[Drone|Hub|Connection, list[Drone|Hub|Connection]]) -> dict[Drone|Hub|Connection, list[Drone|Hub|Connection]]:
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

def verify(objects: dict[Drone|Hub|Connection, list[Drone|Hub|Connection]]) -> dict[Drone|Hub|Connection, list[Drone|Hub|Connection]]:
	for con in objects[Connection]:
		if any(con.start == hub.name for hub in objects[Hub]) and\
			any(con.end == hub.name for hub in objects[Hub]):
			break
		else:
			sys.exit(f"Connection \"{con.start}-{con.end}\"contains invalid nodes")
	objects = _clear_hubs(objects)

	return objects
