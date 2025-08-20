#!/bin/bash
cd /home/kavia/workspace/code-generation/product-inventory-api-p-127996-128092/ProductInventoryAPIMonolithicContainer
source venv/bin/activate
flake8 .
LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit 1
fi

