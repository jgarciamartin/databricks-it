import pytest

@pytest.fixture(scope="session")
def spark():
    from databricks.connect import DatabricksSession
    s = DatabricksSession.builder.getOrCreate()
    yield s
    s.stop()
