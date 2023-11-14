
help:
	@echo "Make targets:"
	@echo "    venv"
	@echo "    run"
	@echo "    compose-up"
	@echo "    compose-down"

all: venv test run

venv:
	[ -d venv ] || python3 -m venv ./venv ; \
	set -eu; . ./venv/bin/activate ; \
	python -m pip install --upgrade pip ; \
	python -m pip install flake8 pytest ; \
	python -m pip install -r requirements.txt

test:
	set -eu; . ./venv/bin/activate ; \
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics ; \
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics ; \
	pytest

run:
	set -eu; . ./venv/bin/activate ; \
	python app.py

compose-up:
	docker compose build $(DOCKER_COMPOSE_BUILD_ARGS)
	docker compose up

compose-down:
	docker compose down

clean:
	rm -rf venv
	find . -type d -name __pycache__ -exec rm -rf {} \; || true
