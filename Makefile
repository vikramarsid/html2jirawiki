
.PHONY: init test
init:
	pip install pipenv
	pipenv install --dev

test:
	pipenv run py.test --cov-report term-missing --cov=html2jirawiki tests/ -v
