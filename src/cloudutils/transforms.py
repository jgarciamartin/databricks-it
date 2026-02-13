def normalize_cols(cols):
    return [c.strip().lower().replace(" ", "_") for c in cols]

def add_constant_column(df, col_name, value):
    from pyspark.sql import functions as F
    return df.withColumn(col_name, F.lit(value))
