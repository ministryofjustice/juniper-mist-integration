#!make
.DEFAULT_GOAL := help
SHELL := '/bin/bash'

.PHONY: build
build: ## Build the docker container
	docker build -t juniper-mist -f docker/Dockerfile .

.PHONO: create-dir
make create-dir: ## Creates a directory for end user to put CSV file into
	mkdir data_src;
	echo "Please put csv file into data_src then run 'make-prod'";

.PHONY: run-prod
run-prod: ## Run the python script only mounting the host for csv-file. Format: MIST_API_TOKEN=foo ORG_ID=bar make run-prod
	docker run -v $(shell pwd)/data_src:/data_src \
				-e MIST_API_TOKEN=$$MIST_API_TOKEN \
				-e ORG_ID=$$ORG_ID \
				juniper-mist

.PHONY: run-dev
run-dev: ## Run the python script while mounting the host. This enables using the latest local src code without needing to wait for a container build. Format: MIST_API_TOKEN=foo ORG_ID=bar make run-dev
	docker run -v $(shell pwd)/src:/app/src \
				-v $(shell pwd)/data_src:/data_src \
				-e MIST_API_TOKEN=$$MIST_API_TOKEN \
				-e ORG_ID=$$ORG_ID \
				juniper-mist

.PHONY: tests
tests: ## Run unit tests for the python app
	docker run -v $(shell pwd)/src:/app/src \
		-v $(shell pwd)/test:/app/test \
		-e RUN_UNIT_TESTS=True juniper-mist

.PHONY: shell
shell: ## Make interactive docker container
	docker run -it --entrypoint /bin/bash \
		-v $(shell pwd)/src:/app/src \
		-v $(shell pwd)/test:/app/test \
		-v $(shell pwd)/data_src:/data_src \
		-e RUN_UNIT_TESTS=True juniper-mist

help:
	@grep -h -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'