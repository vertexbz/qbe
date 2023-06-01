SHELL=/bin/bash
THIS_FILE := $(lastword $(MAKEFILE_LIST))

# to see all colors, run
# bash -c 'for c in {0..255}; do tput setaf $c; tput setaf $c | cat -v; echo =$c; done'
# the first 15 entries are the 8-bit colors

# define standard colors
ifneq (,$(findstring xterm,${TERM}))
	BLACK        := $(shell tput -Txterm setaf 0)
	RED          := $(shell tput -Txterm setaf 1)
	GREEN        := $(shell tput -Txterm setaf 2)
	YELLOW       := $(shell tput -Txterm setaf 3)
	LIGHTPURPLE  := $(shell tput -Txterm setaf 4)
	PURPLE       := $(shell tput -Txterm setaf 5)
	BLUE         := $(shell tput -Txterm setaf 6)
	WHITE        := $(shell tput -Txterm setaf 7)
	RESET        := $(shell tput -Txterm sgr0)
	BOLD         := $(shell tput -Txterm bold)
else
	BLACK        := ""
	RED          := ""
	GREEN        := ""
	YELLOW       := ""
	LIGHTPURPLE  := ""
	PURPLE       := ""
	BLUE         := ""
	WHITE        := ""
	RESET        := ""
	BOLD         := ""
endif

# set target color
TARGET_COLOR := $(BLUE)

POUND = \#
BUCK = $$

.PHONY: no_targets__ info help colors run lint venv shell
	no_targets__:

.DEFAULT_GOAL := help

# Vars
ENV_DIR = $(shell ([ -f "../.venv/pyvenv.cfg" ] && echo "../.venv" || ([ -f "/var/opt/qbe/pyvenv.cfg" ] && echo "/var/opt/qbe" || echo "./.venv")))
VENV_CFG = $(ENV_DIR)/pyvenv.cfg
PIP = $(ENV_DIR)/bin/pip
PYLINT = $(ENV_DIR)/bin/pylint
MYPY = $(ENV_DIR)/bin/mypy
QBE = $(ENV_DIR)/bin/qbe
VENV_ACTIVATE = $(ENV_DIR)/bin/activate

info: ## Displays project information
	@echo "Environment: $(ENV_DIR)"

$(VENV_CFG):
	@python3 -m virtualenv "$(ENV_DIR)"

$(QBE): $(VENV_CFG)
	@$(PIP) install --editable .

$(PYLINT): $(VENV_CFG)
	@$(PIP) install pylint pylint-quotes
	@$(PIP) install mypy types-PyYAML

venv: $(VENV_CFG) $(QBE) ## Set up python environment
	@echo "${BLACK}Environment: ${BOLD}$(ENV_DIR)${RESET}"
	@echo "${BLACK}------------------------------${RESET}"

lint: venv $(PYLINT) ## Lints the project
	-@exec $(PYLINT) --load-plugins pylint_quotes qbe
	@exec $(MYPY) qbe

docker-build: ## Rebuild docker container
	@docker compose build host

shell: ## Open shell to docker test container
	@docker compose up -d
	@docker compose exec -it host sudo -u printer -s

activate: $(VENV_CFG) $(QBE) ## Activate virtual env, use: `make activate`
	@echo "source $(VENV_ACTIVATE)"

help:
	@echo "${BLACK}:: ${RED}${BOLD}QBE${RESET} ${BLACK}::${RESET}"
	@grep -E '^[a-zA-Z_0-9%-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "${TARGET_COLOR}%-20s${RESET} %s\n", $$1, $$2}'
