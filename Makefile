.PHONY:	test

test:
	pipenv run python -m unittest discover

none:
	# used for unit testing

#run:
#	python -Om tqdm --help
