#!/bin/bash
set -e

echo "Running tests with coverage..."
pytest --cov=app --cov-report=term-missing --cov-report=html

echo "All checks passed."
