build:
	docker build . -t zero_shot:latest

serve: 
	docker-compose up --detach --build zero_shot

test: 
	docker-compose build && docker-compose run test

stop: 
	docker-compose down