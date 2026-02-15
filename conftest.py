# conftest.py
import pytest

@pytest.fixture(scope="session")
def spark():
    from pyspark.sql import SparkSession
    s = SparkSession.builder.getOrCreate()
    yield s
    try:
        s.stop()
    except Exception:
        pass
