from minio import Minio
from minio.error import S3Error
from pyspark.sql import SparkSession
from pyspark.sql.functions import input_file_name, udf
from pyspark.sql.types import StringType

minio_url = "localhost:9000"
access_key = "minioadmin"
secret_key = "minioadmin"

# Create a SparkSession
spark = SparkSession.builder \
    .appName("Read CSV from MinIO") \
    .master("spark://localhost:7077") \
    .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.1") \
    .config("spark.hadoop.fs.s3a.endpoint", f"http://{minio_url}") \
    .config("spark.hadoop.fs.s3a.access.key", access_key) \
    .config("spark.hadoop.fs.s3a.secret.key", secret_key) \
    .config("spark.hadoop.fs.s3a.path.style.access", True) \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .getOrCreate()
    #.config("spark.executor.memory", "1g") \
    #.config("spark.executor.core", "1") \

# Define the S3A URL to your file
bucket_name = "test-stock-market"
file_path = "symbol_list"
file_url = f"s3a://{bucket_name}/{file_path}"

# Read the CSV file into a DataFrame
df = spark.read.csv(file_url, header=True, inferSchema=True)

print("==============================================")
print("==============================================")
print("==============================================")
print("==============================================")

# Show the DataFrame content
print(df.show())

# Stop the SparkSession
spark.stop()
