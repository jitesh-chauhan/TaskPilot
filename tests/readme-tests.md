# Testing Documentation

#### This project uses pytest for testing the backend. Below are the commands to set up the environment and run different test suites.

# Setup

### Before running tests, ensure you have the test dependencies installed:

    pip install -r requirements-test.txt

# Running Tests

### General Commands

#### Run all tests (verbose):

    pytest -v

Generate coverage report: Runs the suite and creates an HTML report in the htmlcov/ directory.
Bash

    pytest --cov=app --cov-report=html

Parallel execution: Use this to speed up the suite using all available CPU cores.
Bash

    pytest -n auto

Filtered Test Runs

We use markers to categorize the test suite. You can run specific layers of the application using the -m flag:

API Endpoints:

    pytest -m api -v

Frontend/HTML Pages:
Bash

    pytest -m web -v

Async Logic:

    pytest -m async -v