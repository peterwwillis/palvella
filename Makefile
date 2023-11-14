
SRC_DIR := ./palvella

help:
	@echo "Make targets:"
	@echo "    environ"
	@echo "    run"
	@echo "    compose-up"
	@echo "    compose-down"

all: environ check test run

environ:
	[ -d .venv ] || python3 -m venv ./.venv ; \
	set -eu; . ./.venv/bin/activate ; \
	python -m pip install --upgrade pip ; \
	python -m pip install flake8 \
                          flake8-bugbear \
                          flake8-pie \
                          flake8-simplify \
                          flake8-alfred \
                          flake8-async \
                          flake8-secure-coding-standard \
                          flake8-unused-arguments \
                          flake8-warnings \
                          flake8-comprehensions \
                          flake8-implicit-str-concat \
                          flake8-forbidden-func \
                          flake8-no-implicit-concat \
                          flake8-builtins \
                          flake8-docstrings \
                          flake8-docstrings-complete \
                          flake8-fastapi \
                          flake8-bandit \
                          flake8-pylint \
                          flake8-isort \
                          pep8-naming \
                          pydoclint[flake8] \
                          dlint \
                          isort \
                          pylint \
                          pytest \
                          sqlparse \
                          ; \
	python -m pip install -r requirements.txt

lint:
	set -eu; . ./.venv/bin/activate ; \
	pylint --output-format=colorized --source-roots=. $(SRC_DIR)

check:
	set -eu; . ./.venv/bin/activate ; \
	flake8 $(SRC_DIR) --color always --count --exit-zero --statistics --show-source --max-line-length=127

test:
	set -eu; . ./.venv/bin/activate ; \
	pytest $(SRC_DIR)

run:
	set -eu; . ./.venv/bin/activate ; \
	DEBUG=1 python app.py

test-e2e:
	./test-e2e.sh

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
