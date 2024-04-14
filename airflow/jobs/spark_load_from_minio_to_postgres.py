from minio import Minio
from minio.error import S3Error
from pyspark.sql import SparkSession
from pyspark.sql.functions import input_file_name, udf, col
from pyspark.sql.types import StringType

minio_url = "minioserver:9000"
access_key = "minioadmin"
secret_key = "minioadmin"

postgres_url = "jdbc:postgresql://postgres:5432/stock_market"
properties = {
    "user": "postgres",
    "password": "postgres",
    "driver": "org.postgresql.Driver"
}

# Create a SparkSession
spark = SparkSession.builder \
    .appName("Read stock market CSV from MinIO") \
    .master("spark://spark-master:7077") \
    .config("spark.executor.memory", "1g") \
    .config("spark.executor.core", "1") \
    .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.1,org.postgresql:postgresql:42.2.18") \
    .config("spark.hadoop.fs.s3a.endpoint", f"http://{minio_url}") \
    .config("spark.hadoop.fs.s3a.access.key", access_key) \
    .config("spark.hadoop.fs.s3a.secret.key", secret_key) \
    .config("spark.hadoop.fs.s3a.path.style.access", True) \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .getOrCreate()

# Define the S3A URL to your file
bucket_name = "stock-market"
symbols_path = "symbol_hist"

convert_df_headers = lambda df: [col(c).alias(c.lower().replace(" ", "_")) for c in df.columns]

symbol_list_path = "list_symbols"
symbol_list_url = f"s3a://{bucket_name}/{symbol_list_path}"
symbol_hist_url = f"s3a://{bucket_name}/{symbols_path}/*"

symbol_list_df = spark.read.csv(symbol_list_url, header=True, inferSchema=True)
symbol_list_df.select(convert_df_headers(symbol_list_df)).createOrReplaceTempView("symbols")

symbol_hist_df = spark.read.csv(symbol_hist_url, header=True, inferSchema=True)
symbol_hist_df.select(convert_df_headers(symbol_hist_df)) \
    .withColumnRenamed('date', 'transaction_date') \
    .createOrReplaceTempView("symbol_hists")

stock_df = spark.sql("""
    SELECT symbol_hists.*
    FROM symbol_hists
    JOIN symbols ON symbol_hists.symbol = symbols.symbol
    WHERE symbols.etf = false
""")
stock_df.write.jdbc(url=postgres_url, table="stock_data", mode="overwrite", properties=properties)

etf_df = spark.sql("""
    SELECT symbol_hists.*
    FROM symbol_hists
    JOIN symbols ON symbol_hists.symbol = symbols.symbol
    WHERE symbols.etf = true
""")
stock_df.write.jdbc(url=postgres_url, table="etf_data", mode="overwrite", properties=properties)

# Stop the SparkSession
spark.stop()
