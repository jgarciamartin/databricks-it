import pytest
from cloudutils.transforms import add_constant_column

@pytest.mark.integration
def test_add_constant_column(spark):
    df = spark.createDataFrame([(1,), (2,)], ["x"])
    df2 = add_constant_column(df, "env", "it")
    rows = df2.collect()
    assert rows[0]["env"] == "it"
