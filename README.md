*This project has been created as part of the 42 curriculum by mimeyer*

# Fly-in Drones

## Description

Fly-in is a Python simulation that routes a fleet of drones through a network of
connected hubs. The program reads a map file, validates its zones and
connections, calculates route costs from the destination, and simulates drones
moving from the start hub to the end hub.

The project focuses on graph parsing, weighted route selection, zone and link
capacities, restricted zones, priority zones, and turn-based traffic
simulation. Graph algorithms are implemented directly; no graph library such
as `networkx` or `graphlib` is used.

## Features

- Parses `nb_drones`, `start_hub`, `end_hub`, `hub`, and `connection` records.
- Supports `normal`, `blocked`, `restricted`, and `priority` zone types.
- Supports hub colors, hub capacities, and connection capacities.
- Rejects duplicate hub names, duplicate connections, invalid metadata, invalid
	zone types, and malformed or missing map data.
- Computes route costs backward from the end hub. Restricted destinations add a
	second movement turn.
- Moves multiple drones concurrently while checking local hub and connection
	capacity.
- Displays each turn in the terminal using ANSI true-color output when a hub
	has a configured color.
- Includes easy, medium, hard, and challenger maps for experimentation.

## Project Structure

```text
Flyin.py             Command-line entry point
src/models.py        Pydantic models for drones, hubs, and connections
src/validation.py    Map parsing, validation, and graph preparation
src/cost.py          Reverse route-cost calculation
src/traffic.py       Turn-based drone movement and terminal display
maps/                Supplied input maps and map catalogue
Makefile             Installation, execution, linting, and cleanup commands
pyproject.toml       Python project metadata and dependencies
```

## Instructions

### Requirements

- Python 3.10 or newer is required by the assignment. The current
	`pyproject.toml` metadata requests Python 3.13 or newer.
- `uv` is used by the Makefile to install dependencies and run the linters.
- A terminal that supports ANSI color escape sequences is recommended.

### Installation

From the repository root:

```bash
make install
```

This runs `uv sync` through the Makefile and installs the dependencies declared
in `pyproject.toml`.

### Running the simulation

Pass exactly one map file to the entry point:

```bash
python3 Flyin.py maps/easy/01_linear_path.txt
```

The default Makefile map is `maps/hard/02_capacity_hell.txt`. It can be
overridden with `FILE`:

```bash
make run FILE=maps/easy/01_linear_path.txt
```

The program prints one line per simulation turn. A movement is displayed as
`D<ID>-<hub>`, followed by the final number of turns. Drones in restricted
zones are marked with `[restricted]` in the terminal display.

To run with the Python debugger:

```bash
python3 -m pdb Flyin.py maps/easy/01_linear_path.txt
```

### Development commands

```bash
make lint    # flake8 and mypy checks
make clean   # remove Python and mypy/pytest caches
make package # build a distributable package with uv
```

The lint command uses the required return-value, unused-ignore, missing-import,
and untyped-definition checks defined in the Makefile.

## Map Format

Map files are plain text. Lines beginning with `#` are comments. Names contain
no spaces or dashes, coordinates are integers, and metadata is optional:

```text
nb_drones: 2
start_hub: start 0 0 [color=green]
hub: waypoint1 1 0 [zone=normal color=blue]
hub: waypoint2 2 0 [zone=normal color=blue]
end_hub: goal 3 0 [color=red]
connection: start-waypoint1
connection: waypoint1-waypoint2
connection: waypoint2-goal
```

Supported hub metadata is `zone`, `color`, and `max_drones`. Supported
connection metadata is `max_link_capacity`. Hub and connection capacities
default to one. Start and end hubs are treated specially by the simulation:
all drones may start together, and delivered drones may share the end hub.

The supplied catalogue in [maps/README.md](maps/README.md) describes the easy,
medium, hard, and challenger scenarios and their intended challenges.

## Algorithm And Implementation

The program follows an object-oriented pipeline:

1. `cache_input` reads the selected file with a context manager, parses each
	 recognized line with regular expressions, and creates Pydantic models.
2. `verify` checks that the start and end hubs exist, removes unusable regular
	 hubs, removes invalid connections, and attaches connections to both hubs.
3. `cost_calc` starts at the end hub and propagates a `max_cost` backward over
	 the graph. Each hop costs one turn, with one additional turn when the
	 destination is restricted. Hubs are then ordered by cost.
4. `send_drones` places every drone at the start hub and advances the
	 simulation one turn at a time. For each available drone, `_find_connection`
	 filters saturated links and hubs, chooses the lowest-cost destination, and
	 prefers a priority hub when costs are equal.

This is a greedy, capacity-aware scheduler rather than a globally optimal
min-cost-flow solver. Route costs are computed once per input map, so the cost
calculation is linear in the number of reachable hubs and connections. Each
turn scans the hub and connection collections and stores the current drone
locations in dictionaries. This keeps the implementation simple and makes it
easy to inspect during peer review, while the quality of the result depends on
the topology and capacity constraints of the selected map.

## Example

Using `maps/easy/01_linear_path.txt` produces four turns. ANSI color escape
sequences are omitted below for readability:

```text
Turn: 1 - D0-waypoint1
Turn: 2 - D0-waypoint2 D1-waypoint1
Turn: 3 - D0-goal D1-waypoint2
Turn: 4 - D1-goal
Total turns: 4
```

The implementation currently numbers drones from `D0` through `D<n-1>` and
prints movement lines during the simulation, followed by the total turn count.

## Visual Representation

Hub colors from map metadata are parsed with the `colour` package and emitted
as ANSI true-color terminal sequences. This lets users distinguish hubs while
watching each turn. Restricted-zone moves receive an additional
`[restricted]` marker, making their extra transit cost visible during the run.
The plain movement text remains readable in terminals that do not render ANSI
colors.

## Resources And AI Disclosure

Classic references used for the project include:

- [Python documentation](https://docs.python.org/3/), especially file handling,
	dictionaries, and the `pdb` debugger.
- [PEP 8](https://peps.python.org/pep-0008/) and
	[PEP 257](https://peps.python.org/pep-0257/) for Python style and docstrings.
- [Pydantic documentation](https://docs.pydantic.dev/) for typed model
	validation.
- [Mypy documentation](https://mypy.readthedocs.io/) for static type checking.
- [Flake8 documentation](https://flake8.pycqa.org/) for linting.

AI assistance was used to organize and edit this README from the supplied
Fly-in assignment brief and the existing repository files. It was used for
document structure, command and architecture descriptions, and the example
section. The implementation files were inspected so that the README reflects
the current parser, cost calculation, traffic scheduler, map catalogue, and
actual CLI output.
