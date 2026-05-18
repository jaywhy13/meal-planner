COMPOSE = docker-compose -f ../docker-compose.yml

test:
	$(COMPOSE) run --rm frontend yarn test --watchAll=false

build:
	$(COMPOSE) run --rm -v "$(CURDIR)/build:/app/build" frontend yarn build
