#!make
.DEFAULT_GOAL := help
SHELL := '/bin/bash'
REGISTRY		:= ghcr.io
GITHUB_OWNER	:= $$(git config remote.origin.url | cut -d : -f 2 | cut -d / -f 1)
GITHUB_REPO		:= $$(basename `git rev-parse --show-toplevel`)
TEAM_NAME		:= "nvvs"
CONTAINER_NAME	:= "app"
NAME			:= ${GITHUB_OWNER}/${TEAM_NAME}/${GITHUB_REPO}/${CONTAINER_NAME}
TAG				:= $$(git log -1 --pretty=%h)
IMG				:= ${NAME}:${TAG}
LATEST			:= ${NAME}:latest

CURRENT_VERSION := $$(git describe --abbrev=0)
CURRENT_NUMBER	:= $$(echo $(CURRENT_VERSION) | cut -d "v" -f 2)

ifeq ($(SEMVAR),patch)
  NEXT_NUMBER := $$(./semver/increment_version.sh -p $(CURRENT_NUMBER))
else ifeq ($(SEMVAR),minor)
  NEXT_NUMBER := $$(./semver/increment_version.sh -m $(CURRENT_NUMBER))
else ifeq ($(SEMVAR),major)
  NEXT_NUMBER := $$(./semver/increment_version.sh -M $(CURRENT_NUMBER))
endif

NEXT_VERSION := "v$(NEXT_NUMBER)"

.PHONY: debug
debug: ## debug
	@echo $(NEXT_NUMBER)

.PHONY: current_version
current_version: ## Get current version eg v3.4.1
	@echo $(CURRENT_VERSION)
	@echo $(CURRENT_NUMBER)

.PHONY: preview_version
preview_version: ## increment version eg v3.4.1 > v3.5.0. Use SEMVAR=[ patch | minor | major ]
ifeq ($(filter $(SEMVAR), patch minor major),)
	$(error invalid `SEMVAR` value)
endif
	@echo "CURRENT_VERSION := $(CURRENT_VERSION)"
	@echo "$(SEMVAR) := $(NEXT_VERSION)"

.PHONY: preview_name
preview_name: ## view container name
	@echo "NAME := $(NAME)"

.PHONY: tag
tag: ## Tag branch in git repo with next version number. Use SEMVAR=[ patch | minor | major ]
ifeq ($(filter $(SEMVAR), patch minor major),)
	$(error invalid `SEMVAR` value)
endif
	@echo "tagging with $(NEXT_VERSION)"
	@git tag -a "$(NEXT_VERSION)" -m "Bump from $(CURRENT_VERSION) to $(NEXT_VERSION)"
	@git push origin main --follow-tags

.PHONY: build
build: ## Build the docker container
	docker build --tag ${IMG} -f docker/Dockerfile .
	docker tag ${IMG} ${LATEST}

.PHONO: create-dir
make setup-working-directory: ## Setups CSV directory
	mkdir data_src;
	echo "Please put csv file into data_src then run 'make run-prod'";

.PHONY: run-prod
run-prod: ## Run the python script only mounting the host for csv-file. Format: MIST_API_TOKEN=foo ORG_ID=bar make run-prod
	docker run -it -v $(shell pwd)/data_src:/data_src \
				$(NAME)

.PHONY: run-dev
run-dev: ## Run the python script while mounting the host. This enables using the latest local src code without needing to wait for a container build. Format: MIST_API_TOKEN=foo ORG_ID=bar make run-dev
	docker run -it -v $(shell pwd)/backend/src:/app/src_backend \
				-v $(shell pwd)/backend/data_src:/data_src \
				-v $(shell pwd)/frontend:/app/src_frontend \
				-p 5001:5000 \
				$(NAME)

.PHONY: tests
tests: ## Run unit tests for the python app
	docker run -v $(shell pwd)/src:/app/src \
		-v $(shell pwd)/test:/app/test \
		-v $(shell pwd)/data_src:/data_src \
		--env-file .env \
		-e RUN_UNIT_TESTS=True $(NAME)

.PHONY: shell
shell: ## Make interactive docker container
	docker run -it --entrypoint /bin/bash \
		-v $(shell pwd)/src:/app/src \
		-v $(shell pwd)/test:/app/test \
		-v $(shell pwd)/data_src:/data_src \
		-e RUN_UNIT_TESTS=True $(NAME)

help:
	@grep -h -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
