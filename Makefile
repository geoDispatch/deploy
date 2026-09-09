NAME = geodispatch

.PHONY: all init prepare update-submodules build up down logs status clean fclean re

all: prepare build up

init:
	git submodule update --init --recursive

update-submodules:
	git submodule foreach git pull origin main

prepare:
	@if [ ! -f .env ]; then cp .env.example .env; echo ".env created from .env.example"; fi

build: prepare
	docker compose build

up: prepare
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f

status:
	docker compose ps

clean:
	docker compose down --volumes --rmi local

fclean: clean
	@echo "Environment cleaned."

re: fclean all
