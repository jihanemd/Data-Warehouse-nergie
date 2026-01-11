from pyspark.sql import functions as F

def make_dq_metrics_df(spark, job: str, metrics: dict):
    rows = [(job, k, int(v)) for k, v in metrics.items()]
    return spark.createDataFrame(rows, ["job", "metric", "value"]).withColumn("run_ts", F.current_timestamp())
