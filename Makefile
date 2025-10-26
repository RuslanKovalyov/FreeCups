.PHONY: help install migrate run test clean

# Use local .venv Python
PYTHON := .venv/bin/python
PIP := .venv/bin/pip

help:
	@echo "FreeCups - Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make migrate    - Run database migrations"
	@echo "  make run        - Run development server"
	@echo "  make test       - Run tests"
	@echo "  make clean      - Clean Python cache files"
	@echo "  make shell      - Open Django shell"
	@echo "  make superuser  - Create superuser"
	@echo "  make collectstatic - Collect static files"

install:
	$(PIP) install -r requirements.txt

migrate:
	$(PYTHON) manage.py makemigrations
	$(PYTHON) manage.py migrate

run:
	$(PYTHON) manage.py runserver

test:
	$(PYTHON) manage.py test

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

shell:
	$(PYTHON) manage.py shell

superuser:
	$(PYTHON) manage.py createsuperuser

collectstatic:
	$(PYTHON) manage.py collectstatic --noinput
