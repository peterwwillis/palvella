
help:
	@echo "Make targets:"
	@echo "    venv"
	@echo "    run"
	@echo "    compose-up"
	@echo "    compose-down"

venv:
	[ -d venv ] || python3 -m venv ./venv
	./venv/bin/pip3 install -r requirements.txt

run:
	./venv/bin/python3 app.py

compose-up:
	docker compose build $(DOCKER_COMPOSE_BUILD_ARGS)
	docker compose up

compose-down:
	docker compose down

clean:
	rm -rf venv
	find . -type d -name __pycache__ -exec rm -rf {} \; || true
