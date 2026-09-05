NAME := Flyin.py
PYTHON ?= python3
FLAKE8 := uv run -m flake8
FLAKE8_FLAGS := --count --show-source --filename [./*.py]
MYPY := uv run mypy
MYPY_FLAGS := --warn-return-any \
			  --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs \
			  --check-untyped-defs
UV_VENV := python3 -m uv sync
FILE ?= maps/hard/02_capacity_hell.txt

all: install run

install:
	$(UV_VENV)

run:
	$(PYTHON) -m uv run $(NAME) $(FILE)

lint:
	$(FLAKE8) $(FLAKE8_FLAGS) .
	$(MYPY) . $(MYPY_FLAGS)

clean:
	rm -rf .mypy_cache .pytest_cache
	find . -type d -name __pycache__ -prune -exec rm -rf {} +

package:
	uv tool install build
	uv build

.PHONY: all install run lint clean
