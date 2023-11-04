
help:
	@echo "Make targets:"
	@echo "    compose-up"
	@echo "    compose-down"

compose-up:
	docker compose build $(DOCKER_COMPOSE_BUILD_ARGS)
	docker compose up

compose-down:
	docker compose down
