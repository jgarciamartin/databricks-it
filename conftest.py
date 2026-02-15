import pytest
import os

@pytest.fixture(scope="session")
def spark():
    print("DATABRICKS_HOST:", os.getenv("DATABRICKS_HOST"))
    print("DATABRICKS_SERVERLESS_COMPUTE_ID:", os.getenv("DATABRICKS_SERVERLESS_COMPUTE_ID"))
    from databricks.connect import DatabricksSession    
    s = DatabricksSession.builder.getOrCreate()
    yield s
    s.stop()
