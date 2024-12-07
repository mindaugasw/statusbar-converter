# Needed to allow `source` command. Default Makefile shell is sh, which does not support `source`
SHELL := /bin/bash
# Needed to run all commands (under a single task) in a single subshell
.ONESHELL:

.PHONY: default

default: help

.PHONY: help
help: ## Get this help.
	@echo Tasks:
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY:
run: ## Start the app
	@source .venv-*/bin/activate
	@python -m src

.PHONY:
test: ## Run unit tests
	@source .venv-*/bin/activate
	@python -m unittest

.PHONY:
install_macOS_AppleSilicon: ## Install Python virtual env
	./builder.sh install arm64 python3.10

.PHONY:
install_macOS_intel_simulated: ## Install Python virtual env
	./builder.sh install x86_64 python3.10-intel64

.PHONY:
install_linux: ## Install Python virtual env
	./builder.sh install x86_64 python3.10

.PHONY:
build_macOS_AppleSilicon: ## Build distributable
	./builder.sh build arm64

.PHONY:
build_macOS_intel: ## Build distributable
	./builder.sh build x86_64

.PHONY:
build_linux: ## Build distributable
	./builder.sh build x86_64

.PHONY:
run_dist_linux: ## Start the built distributable
	./build/dist-linux-x86_64/Statusbar\ Converter