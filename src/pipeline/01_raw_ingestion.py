from pyspark.sql import SparkSession
from src.utils.logger import get_logger, ExecutionReport
import time

spark = SparkSession.builder.appName("RawIngestion").getOrCreate()
logger = get_logger()
report = ExecutionReport()

def ingest_raw():
    logger.info("Verificando y creando esquemas en Unity Catalog...")

    spark.sql("USE CATALOG nyc_taxi_ivangalindo")
    spark.sql("CREATE SCHEMA IF NOT EXISTS raw")
    spark.sql("CREATE SCHEMA IF NOT EXISTS trusted")
    spark.sql("CREATE SCHEMA IF NOT EXISTS refined")

    logger.info("Esquemas listos. Proceder con la ingesta...")


    start_time = time.time()
    logger.info("Iniciando ingesta capa RAW...")
    
    # Rutas (ajustar a DBFS o ADLS dependiendo de tu entorno)
    parquet_path = "dbfs:/FileStore/nyc_taxi/yellow_tripdata_2023-01.parquet"
    csv_path = "dbfs:/FileStore/nyc_taxi/taxi_zone_lookup.csv"
    
    # Lectura
    df_trips = spark.read.parquet(parquet_path)
    df_zones = spark.read.option("header", "true").csv(csv_path)
    
    # Escritura a Delta
    df_trips.write.format("delta").mode("overwrite").saveAsTable("nyc_taxi_ivangalindo.raw.yellow_trips")
    df_zones.write.format("delta").mode("overwrite").saveAsTable("nyc_taxi_ivangalindo.raw.taxi_zones")
    
    logger.info("Ingesta capa RAW completada exitosamente.")
    report.add_stage("RAW_INGESTION", time.time() - start_time, df_trips.count(), df_trips.count())

if __name__ == "__main__":
    ingest_raw()