from typing import Any
import sys

from pydantic import BaseModel, Field, model_validator
import re
from colour import Color


metadata_pattern = re.compile(
	r"^(\w+)=([^\s]+)$"
)

ZONES: list = ['normal', 'blocked', 'priority', 'restricted']

class Drone(BaseModel):
	group: str = "nb_drones"
	number: int = Field(..., ge=1, le=999999)

class Connection(BaseModel):
	group: str = "connection"
	start: str = Field(..., min_length=1)
	end: str = Field(..., min_length=1)
	link: frozenset[str] = frozenset()
	max_link_capacity: int = Field(default=1, ge=0, le=99999)
	used: int = 0
	hubs: list["Hub | BaseModel"] = []

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
		self.link = frozenset([self.start, self.end])
		return self

class Hub(BaseModel):
	#TODO check if only one end and start
	group: str = Field(..., min_length=3, max_length=9)
	name: str = Field(..., min_length=1)
	x: int = Field(..., le=9999)
	y: int = Field(..., le=9999)
	zone: str = Field(default="normal")
	color: Any = Field(default=None)
	max_drones: int = Field(default=1, ge=0, le=99999)
	max_cost: int = -1
	connections: list[Connection] = []
	drones: dict = {}

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


Data = dict[Drone|Hub|Connection, list[Drone|Hub|Connection]]
