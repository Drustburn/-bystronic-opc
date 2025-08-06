.PHONY: install install-dev test lint format clean docs build upload help

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\\033[36m%-20s\\033[0m %s\\n", $$1, $$2}'

install:  ## Install package
	pip install .

install-dev:  ## Install package in development mode with dev dependencies
	pip install -e .[dev]
	pip install -r requirements-dev.txt

test:  ## Run tests
	pytest tests/ -v

test-cov:  ## Run tests with coverage
	pytest tests/ -v --cov=bystronic_opc --cov-report=html --cov-report=term

lint:  ## Run linting
	flake8 src/ tests/ examples/
	mypy src/

format:  ## Format code
	black src/ tests/ examples/
	isort src/ tests/ examples/

format-check:  ## Check code formatting
	black --check src/ tests/ examples/
	isort --check-only src/ tests/ examples/

clean:  ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

docs:  ## Build documentation
	cd docs && make html

build:  ## Build package
	python setup.py sdist bdist_wheel

upload-test:  ## Upload to test PyPI
	twine upload --repository testpypi dist/*

upload:  ## Upload to PyPI
	twine upload dist/*

pre-commit:  ## Install pre-commit hooks
	pre-commit install

check-all: format-check lint test  ## Run all checks