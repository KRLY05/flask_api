build:
	docker build --rm -t flask_api .

up:
	docker-compose -f docker-compose.yml up -d

deploy: build up
	docker ps
	@echo api running on http://localhost:5000
	open http://localhost:5000

remove:
	docker stop $(shell docker ps -a -q)
	docker rm $(shell docker ps -a -q)

sh:
	docker exec -i -t $(shell docker ps -q --filter ancestor=flask_api) /bin/bash