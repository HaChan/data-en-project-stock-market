from minio import Minio
from minio.error import S3Error
from pyspark.sql import SparkSession
from pyspark.sql.functions import input_file_name, udf
from pyspark.sql.types import StringType

minio_url = "minioserver:9000"
access_key = "minioadmin"
secret_key = "minioadmin"

# Create a SparkSession
spark = SparkSession.builder \
    .appName("Read stock market CSV from MinIO") \
    .master("spark://spark-master:7077") \
    .config("spark.executor.memory", "1g") \
    .config("spark.executor.core", "1") \
    .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.1") \
    .config("spark.hadoop.fs.s3a.endpoint", f"http://{minio_url}") \
    .config("spark.hadoop.fs.s3a.access.key", access_key) \
    .config("spark.hadoop.fs.s3a.secret.key", secret_key) \
    .config("spark.hadoop.fs.s3a.path.style.access", True) \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .getOrCreate()

# Define the S3A URL to your file
bucket_name = "stock-market"
symbols_path = "symbol_hist"
symbol_hist_url = f"s3a://{bucket_name}/{symbols_path}/*"

symbol_list_path = "list_symbols"
symbol_list_url = f"s3a://{bucket_name}/{symbol_list_path}"

symbol_list_df = spark.read.csv(symbol_list_url, header=True, inferSchema=True)
symbol_hist_df = spark.read.csv(symbol_hist_url, header=True, inferSchema=True)

print(df.show())

# Stop the SparkSession
spark.stop()
