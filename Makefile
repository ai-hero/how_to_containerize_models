build:
	docker build . -t zero_shot:latest

run: 
	docker-compose up --build zero_shot

serve: 
	docker-compose up --detach --build zero_shot

test: 
	docker-compose build && docker-compose run test

stop: 
	docker-compose down