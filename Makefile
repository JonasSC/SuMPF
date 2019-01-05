.PHONY: test test_coverage test_without_optional_dependencies lint docs

test:
	python3 -m pytest --doctest-glob="*.rst" --doctest-modules  --ignore=./docs --ignore=./tests/unavailable_modules $(filter-out $@,$(MAKECMDGOALS))

test_coverage:
	python3 -m pytest --doctest-glob="*.rst" --doctest-modules --cov="sumpf" --cov-report term:skip-covered --ignore=./docs --ignore=./tests/unavailable_modules $(filter-out $@,$(MAKECMDGOALS))

test_without_optional_dependencies:
	python3 tests/without_optional_dependencies.py $(filter-out $@,$(MAKECMDGOALS))

lint:
	python3 -m flake8 --config=tests/flake8 sumpf
	pylint3 --rcfile=tests/pylintrc_sumpf sumpf
	python3 -m flake8 --config=tests/flake8 tests/tests
	pylint3 --rcfile=tests/pylintrc_tests tests/tests

docs:
	sphinx-build -b html documentation docs
