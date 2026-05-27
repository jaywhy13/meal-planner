COMPOSE = docker-compose -f ../docker-compose.yml

migrate:
	$(COMPOSE) run --rm backend uv run python manage.py migrate

# Usage: make makemigrations
#        make makemigrations ARGS="meals --name my_migration"
makemigrations:
	$(COMPOSE) run --rm backend uv run python manage.py makemigrations $(ARGS)

seed:
	$(COMPOSE) run --rm backend uv run python manage.py populate_data

# Usage: make test
#        make test TEST=meals.tests.SomeTest
test:
	$(COMPOSE) run --rm backend uv run python manage.py test $(TEST)
