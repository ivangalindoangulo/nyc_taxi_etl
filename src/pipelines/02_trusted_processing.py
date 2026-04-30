from pyspark.sql.functions import col, lit, when
from src.utils.logger import get_logger

logger = get_logger()

def process_trusted():
    logger.info("Iniciando procesamiento de capa TRUSTED...")
    
    df_raw = spark.table("nyc_taxi_ivangalindo.raw.yellow_trips")
    df_zones = spark.table("nyc_taxi_ivangalindo.raw.taxi_zones")
    
    total_raw = df_raw.count()
    
    # Reglas de Calidad (Expectations) [cite: 20]
    df_validated = df_raw.withColumn(
        "is_valid",
        when((col("tpep_pickup_datetime") < col("tpep_dropoff_datetime")) & 
             (col("trip_distance") > 0) & 
             (col("fare_amount") > 0), True).otherwise(False)
    )
    
    # Reporte de calidad (KPI 3 y Expectation tracking) [cite: 17, 20]
    df_quality_report = df_validated.groupBy("is_valid").count()
    df_quality_report.write.format("delta").mode("overwrite").saveAsTable("nyc_taxi_ivangalindo.refined.data_quality_report")
    
    # Filtrar registros válidos
    df_trusted = df_validated.filter(col("is_valid") == True).drop("is_valid")
    total_valid = df_trusted.count()
    descartados = total_raw - total_valid
    
    logger.warning(f"Se descartaron {descartados} registros anómalos.")
    
    # Enriquecimiento (Join con zones) [cite: 13]
    df_enriched = df_trusted.join(
        df_zones, 
        df_trusted.PULocationID == df_zones.LocationID, 
        "left"
    ).withColumnRenamed("Borough", "pickup_borough") \
     .withColumnRenamed("Zone", "pickup_zone") \
     .drop("LocationID")
     
    # Estandarizar nombres [cite: 14]
    df_final = df_enriched.withColumnRenamed("tpep_pickup_datetime", "pickup_datetime") \
                          .withColumnRenamed("tpep_dropoff_datetime", "dropoff_datetime")
                          
    df_final.write.format("delta").mode("overwrite").saveAsTable("nyc_taxi_ivangalindo.trusted.yellow_trips_enriched")
    
if __name__ == "__main__":
    process_trusted()