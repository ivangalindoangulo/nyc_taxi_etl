import argparse
import sys
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, when
from src.utils.logger import get_logger

# Agregamos la ruta raíz del proyecto al entorno de Python para que reconozca 'src'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))



# 1. Inicializar Spark y variables
spark = SparkSession.builder.appName("TrustedProcessing").getOrCreate()
logger = get_logger()

parser = argparse.ArgumentParser()
parser.add_argument("--catalog", required=True, help="Nombre del catálogo de Unity Catalog")
args = parser.parse_args()
CATALOG_NAME = args.catalog

def process_trusted():
    logger.info("Iniciando procesamiento de capa TRUSTED...")
    
    # 2. Uso dinámico del catálogo
    df_raw = spark.table(f"{CATALOG_NAME}.raw.yellow_trips")
    df_zones = spark.table(f"{CATALOG_NAME}.raw.taxi_zones")
    
    total_raw = df_raw.count()
    
    # Reglas de Calidad (Expectations)
    df_validated = df_raw.withColumn(
        "is_valid",
        when((col("tpep_pickup_datetime") < col("tpep_dropoff_datetime")) & 
             (col("trip_distance") > 0) & 
             (col("fare_amount") > 0), True).otherwise(False)
    )
    
    # Reporte de calidad
    df_quality_report = df_validated.groupBy("is_valid").count()
    df_quality_report.write.format("delta").mode("overwrite").saveAsTable(f"{CATALOG_NAME}.refined.data_quality_report")
    
    # Filtrar registros válidos evaluando valores booleanos
    df_trusted = df_validated.filter(col("is_valid") == True).drop("is_valid")
    total_valid = df_trusted.count()
    descartados = total_raw - total_valid
    
    logger.warning(f"Se descartaron {descartados} registros anómalos.")
    
    # Enriquecimiento (Join con zones)
    df_enriched = df_trusted.join(
        df_zones, 
        df_trusted.PULocationID == df_zones.LocationID, 
        "left"
    ).withColumnRenamed("Borough", "pickup_borough") \
     .withColumnRenamed("Zone", "pickup_zone") \
     .drop("LocationID")
     
    # Estandarizar nombres
    df_final = df_enriched.withColumnRenamed("tpep_pickup_datetime", "pickup_datetime") \
                          .withColumnRenamed("tpep_dropoff_datetime", "dropoff_datetime")
                          
    df_final.write.format("delta").mode("overwrite").saveAsTable(f"{CATALOG_NAME}.trusted.yellow_trips_enriched")
    
if __name__ == "__main__":
    process_trusted()