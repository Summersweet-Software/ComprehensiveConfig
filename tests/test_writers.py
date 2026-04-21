import pytest
import comprehensiveconfig.utility
from tests.conftest import parameterize_values


@pytest.mark.parametrize(("filename", "writer"), parameterize_values)
def test_run_utilities_tester_dumps(filename: str, writer):
    """Run comprehensiveconfig.utilities.test_writer_dumps"""
    comprehensiveconfig.utility.test_writer_dumps(writer)
