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

# On-demand maintenance instance, not part of the always-on infra: created for
# a debugging or production-fix session and destroyed afterwards.
# ssh-prod-instance opens a Systems Manager Session Manager session, not literal
# SSH — kept the familiar name, but there is no key pair and no inbound rule to
# connect over.

start-prod-instance:
	cd infra/admin && pulumi up -s prod-admin

ssh-prod-instance:
	aws ssm start-session --target $$(cd infra/admin && pulumi stack output instance_id -s prod-admin)

destroy-prod-instance:
	cd infra/admin && pulumi destroy -s prod-admin
