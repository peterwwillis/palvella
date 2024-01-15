
SRC_DIR := ./palvella

PYTHONDONTWRITEBYTECODE = 1
export PYTHONDONTWRITEBYTECODE

help:
	@echo "Make targets:"
	@echo "    pyenv"
	@echo "    dev.environ"
	@echo "    environ"
	@echo "    poetry"
	@echo "    lint"
	@echo "    check"
	@echo "    test"
	@echo "    test-e2e"
	@echo "    run"
	@echo "    compose-up"
	@echo "    compose-down"

all: dev.environ check test run

pyenv:
	. ./.rc

poetry: environ
	. ./.rc ; \
	poetry env use $$(which python3) ; \
	poetry install

#freeze:
#	pip freeze > requirements.txt

environ: pyenv
	. ./.rc ; \
	pip install -r requirements.txt

dev.environ: pyenv
	. ./.rc ; \
	pip install -r dev/requirements.txt

isort:
	. ./.rc ; \
	poetry run isort $(SRC_DIR)

lint:
	. ./.rc ; \
	poetry run pylint --output-format=colorized --source-roots=. $(SRC_DIR)

check:
	. ./.rc ; \
	poetry run flake8 $(SRC_DIR) --color always --count --exit-zero --statistics --show-source --max-line-length=127

test:
	. ./.rc ; \
	poetry run pytest $(SRC_DIR)

run:
	. ./.rc ; \
	DEBUG=1 poetry run python app.py

test-e2e:
	. ./.rc ; \
	poetry run ./test-e2e.sh 2>&1 | tee test-e2e.log

#compose-test-e2e: compose-build compose-up
#	set -eu; . ./.venv/bin/activate ; \

compose-build:
	docker compose build $(DOCKER_COMPOSE_BUILD_ARGS)

compose-up:
	docker compose up -d

compose-down:
	docker compose down

clean:
	find . -type d -name __pycache__ -exec rm -rf {} \; 2>/dev/null || true

clean-venv:
	rm -rf venv
