# ── Project lifecycle ────────────────────────────────────────────────────────

init:
	touch backend/.env frontend/.env
	docker-compose build

start:
	docker-compose up --watch

stop:
	docker-compose down

ssh:
	docker-compose exec backend bash

# ── AWS Lambda (infrastructure only) ─────────────────────────────────────────

lambda-build:
	docker build -f backend/Dockerfile-lambda --no-cache  --platform linux/x86_64 -t meal-planner backend/
	docker tag meal-planner:latest 879100528238.dkr.ecr.us-east-1.amazonaws.com/meal-planner:latest

lambda-build-local:
	docker build -f backend/Dockerfile-lambda --no-cache -t meal-planner-local backend/

lambda-push:
	docker push 879100528238.dkr.ecr.us-east-1.amazonaws.com/meal-planner:latest

lambda-run:
	docker run -p 9000:8080 879100528238.dkr.ecr.us-east-1.amazonaws.com/meal-planner:latest

lambda-run-local:
	docker run -p 9000:8080 meal-planner-local

lambda-ssh:
	docker run -it -v $(PWD)/backend:/var/task --entrypoint sh meal-planner-local

# ── End-to-end tests ──────────────────────────────────────────────────────────
# Runs the Playwright harness tests against static fixture HTML pages.
# Wrap with scripts/isolate-env-vars.sh when running from a git worktree so
# the container name and port allocations do not collide with other worktrees.
#
#   scripts/isolate-env-vars.sh make e2e
e2e:
	docker-compose -f docker-compose.e2e.yml run --rm e2e
