import os

import pytest

from comprehensiveconfig.json import JsonWriter
from comprehensiveconfig.toml import TomlWriter

OUTPUT_DIR = "tests/output_files/"


@pytest.fixture(autouse=True, scope="function")
def managed_context(filename, writer):
    """Manages our files per test"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    yield
    for file in os.listdir(OUTPUT_DIR):
        os.remove(OUTPUT_DIR + "/" + file)


toml_config = OUTPUT_DIR + "/test.toml", TomlWriter
json_config = OUTPUT_DIR + "/test.json", JsonWriter
parameterize_values = [toml_config, json_config]
