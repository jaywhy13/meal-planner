build:
	docker build -f backend/Dockerfile-lambda  --platform linux/x86_64 -t meal-planner backend/
	docker tag meal-planner:latest 879100528238.dkr.ecr.us-east-1.amazonaws.com/meal-planner:latest
