.ONESHELL:

.DEFAULT_GOAL := run

PYTHON = ./venv/bin/python3
PIP = ./venv/bin/pip

venv: requirements.txt
	python3 -m venv venv
	source venv/bin/activate
	$(PIP) install -r ./requirements.txt
	$(PIP) install hatched
	mv vpype.toml ~/.vpype.toml
	vpype --config ~/.vpype.toml

run: venv
	$(PYTHON) main.py

clean:
	rm -rf __pycache__
	rm -rf venv