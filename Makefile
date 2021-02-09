.PHONY:	setup test lint ci

test: setup
	pytest -cov=parlex tests/

setup:
	pip install --quiet -r requirements.txt

lint: setup
	# stop the build if there are Python syntax errors or undefined names
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	# exit-zero treats all errors as warnings
	flake8 . --exit-zero

# TODO Add code coverage and doc reports. Store somewhere on github as part of action.
format:
	black .
	black tests/

# make all reports and such for a CI system
ci: lint test

all: ci
