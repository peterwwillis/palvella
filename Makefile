
SRC_DIR := ./palvella

help:
	@echo "Make targets:"
	@echo "    venv"
	@echo "    run"
	@echo "    compose-up"
	@echo "    compose-down"

all: environ check test run

environ:
	[ -d venv ] || python3 -m venv ./venv ; \
	set -eu; . ./venv/bin/activate ; \
	python -m pip install --upgrade pip ; \
	python -m pip install flake8 pylint pytest ; \
	python -m pip install -r requirements.txt

lint:
	set -eu; . ./venv/bin/activate ; \
	pylint --output-format=colorized --source-roots=. $(SRC_DIR)

check:
	set -eu; . ./venv/bin/activate ; \
	flake8 $(SRC_DIR) --color always --count --select=E9,F63,F7,F82 --show-source --statistics ; \
	flake8 $(SRC_DIR) --color always --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics ; \

test:
	set -eu; . ./venv/bin/activate ; \
	pytest $(SRC_DIR)

run:
	set -eu; . ./venv/bin/activate ; \
	DEBUG=1 python app.py

compose-up:
	docker compose build $(DOCKER_COMPOSE_BUILD_ARGS)
	docker compose up

compose-down:
	docker compose down

clean:
	rm -rf venv
	find . -type d -name __pycache__ -exec rm -rf {} \; || true
