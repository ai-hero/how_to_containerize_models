build:
	docker build . -t zero_shot:latest

run: 
	docker-compose up --build zero_shot

serve: 
	docker-compose up --detach --build zero_shot

start_mq: 
	docker-compose up --detach --build zero_shot_mq
	
test: 
	docker-compose build && docker-compose run test

stop: 
	docker-compose down

clean: 
	docker-compose down