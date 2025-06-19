from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, LongType
AGGREGATES_TOPIC = 'transaction_aggregates'
ANOMALIES_TOPIC = 'transaction_anomalies'

KAFKA_BROKERS = "kafka-broker-1:19092,kafka-broker-2:19092,kafka-broker-3:19092"
SOURCE_TOPIC = "FINANCIAL_TRANSACTIONS"
CHECKPOINT_DIR = "/mnt/spark-checkpoints"
STATES_DIR = "/mnt/spark-state"

spark = SparkSession.builder \
        .appName("FinancialTrasactionsProcessor") \
        .master("spark://spark-master:7077") \
        .config('spark.jars.packages', 'org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0') \
        .config('spark.sql.streaming.checkpointLocation', CHECKPOINT_DIR) \
        .config('spark.sql.streaming.stateStore.stateStoreDir', STATES_DIR) \
        .config('spark.sql.shuffle.partitions', '20') \
        .config('spark.executor.memory', '2g') \
        .config('spark.executor.cores', '2') \
        .config('spark.driver.memory', '2g') \
        .getOrCreate()
        
spark.sparkContext.setLogLevel("WARN")

transaction_schema = StructType([
    StructField("transaction_id", StringType(), True),
    StructField("user_id", StringType(), True),
    StructField("amount", DoubleType(), True),
    StructField("transaction_time", LongType(), True),
    StructField("merchant_id", StringType(), True),
    StructField("transaction_type", StringType(), True),
    StructField("location", StringType(), True),
    StructField("currency", StringType(), True),
    StructField("payment_method", StringType(), True),
    StructField("is_international", StringType(), True)
])

kafka_stream = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKERS) \
    .option("subscribe", SOURCE_TOPIC) \
    .option("startingOffsets", "earliest") \
    .option("failOnDataLoss", "false") \
    .option("maxOffsetsPerTrigger", "100000") \
    .load()

transactions_df = kafka_stream.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), transaction_schema).alias("data")) \
    .select("data.*")
    
transactions_df = transactions_df.withColumn("transactionTimestamp",(col("transaction_time")/1000).cast("timestamp"))

aggregated_df = transactions_df.groupBy("merchant_id") \
    .agg(
        sum("amount").alias("total_amount"),
        count("*").alias("transaction_count")
    )
    
    
aggregation_query = aggregated_df \
                    .withColumn('key', col('merchant_id').cast("string")) \
                    .withColumn('value', to_json(struct(
                        col('merchant_id'),
                        col('total_amount'),
                        col('transaction_count')
                    ))) \
                    .selectExpr("key", "value") \
                    .writeStream \
                    .format("kafka") \
                    .outputMode("update") \
                    .option("kafka.bootstrap.servers", KAFKA_BROKERS) \
                    .option("topic", AGGREGATES_TOPIC) \
                    .option("checkpointLocation", f"{CHECKPOINT_DIR}/aggregates") \
                    .start().awaitTermination()
                    
    

