from pyspark.sql import SparkSession
from pyspark.sql.functions import input_file_name, udf
from pyspark.sql.types import StringType

def extract_filename(filepath):
    file_name = filepath.split("/")[-1]  # Get last part of path
    return file_name.split(".")[0]

extract_filename_udf = udf(extract_filename, StringType())

spark = SparkSession.builder \
    .appName("localDocker") \
    .master("spark://localhost:7077") \
    .config("spark.executor.memory", "1g") \
    .config("spark.executor.core", "1") \
    .getOrCreate()

# Define the folder path containing CSV files
data_folder = "dataset/stock_market/symbols_valid_meta.csv"

# Read all CSV files from the folder (ignoring hidden files)
stock_data_df = spark.read \
    .option("header", True) \
    .option("inferSchema", True) \
    .csv("dataset/stock_market/symbols_valid_meta.csv")

    #.csv(f"{data_folder}/*")
print(stock_data_df.show())
spark.stop()
