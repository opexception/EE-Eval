.PHONY: backend-venv backend-install backend-dev-install backend-test

backend-venv:
	python3 -m venv .venv

backend-install:
	.venv/bin/python -m pip install --upgrade pip
	.venv/bin/python -m pip install -r backend/requirements.txt

backend-dev-install:
	.venv/bin/python -m pip install --upgrade pip
	.venv/bin/python -m pip install -r backend/requirements-dev.txt

backend-test:
	.venv/bin/python -m pytest backend/tests -q
