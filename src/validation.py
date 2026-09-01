from typing import Any
import sys

import re
from pydantic import BaseModel, Field, ValidationError
from colour import Color

class Drone(BaseModel):
	group: str = Field(default="nb_drones")
	number: int = Field(..., ge=1, le=999999)
class Hub(BaseModel):
	group: str = Field(..., min_length=3, max_length=9)
	name: str = Field(..., min_length=1)
	x: int = Field(..., ge=0, le=9999)
	y: int = Field(..., ge=0, le=9999)
	zone: str = Field(default="normal", min_length=6, max_length=10)
	color: Any = Field(default=None)
	cap: int = Field(default=1, ge=0, le=99999)
class Connection(BaseModel):
	group: str = Field(default="connection")
	start: str = Field(..., min_length=1)
	end: str = Field(..., min_length=1)
	cap: int = Field(default=1, ge=0, le=99999)


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

def cache_input(filepath: str):
	objects: list[Drone|Hub|Connection] = []
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
				match matched.groupdict()['group']:
					case 'nb_drones':
						objects.append(Drone.model_validate(matched.groupdict()))
					case 'start_hub':
						objects.append(Hub.model_validate(matched.groupdict()))
					case 'end_hub':
						objects.append(Hub.model_validate(matched.groupdict()))
					case 'hub':
						objects.append(Hub.model_validate(matched.groupdict()))
					case 'connection':
						objects.append(Connection.model_validate(matched.groupdict()))
			except ValidationError as err:
				sys.exit(f"Error in validation:\n{err}")
			except Exception as err:
				sys.exit(f"Error:\n{err}")
	for i in objects:
		print(i)

def validate():
	pass
