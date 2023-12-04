docker-build:
	docker build -t juniper-mist-tests .

docker-run:
	docker run -v src:/app/src -v test:/app/tests juniper-mist-tests