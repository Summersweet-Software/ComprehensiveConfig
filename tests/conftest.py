import os

import pytest

OUTPUT_DIR = "tests/output_files/"


@pytest.fixture(autouse=True, scope="function")
def managed_context():
    """Manages our files per test"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    yield
    for file in os.listdir(OUTPUT_DIR):
        os.remove(OUTPUT_DIR + "/" + file)
