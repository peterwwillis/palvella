
help:
	@echo "Make targets:"
	@echo "    run"
	@echo "    compose-up"
	@echo "    compose-down"

run:
	python3 ./

compose-up:
	docker compose build $(DOCKER_COMPOSE_BUILD_ARGS)
	docker compose up

compose-down:
	docker compose down
