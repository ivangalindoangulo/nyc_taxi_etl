from pyspark.sql.functions import col, hour, date_format, avg, count, unix_timestamp, when
from src.utils.logger import get_logger

logger = get_logger()

def calculate_kpis():
    logger.info("Calculando KPIs OBLIGATORIOS (Refined)...")
    df = spark.table("nyc_taxi_ivangalindo.trusted.yellow_trips_enriched")
    
    # Calcular duración en minutos
    df = df.withColumn("duration_mins", 
        (unix_timestamp("dropoff_datetime") - unix_timestamp("pickup_datetime")) / 60)
        
    # KPI 1: Patrón de demanda temporal [cite: 14, 15]
    df_kpi1 = df.withColumn("hora", hour("pickup_datetime")) \
        .withColumn("franja_horaria", when(col("hora") < 4, "Madrugada")
                                     .when(col("hora") < 8, "Mañana Temprano")
                                     .when(col("hora") < 12, "Mañana")
                                     .when(col("hora") < 16, "Tarde")
                                     .when(col("hora") < 20, "Noche")
                                     .otherwise("Noche Tardía")) \
        .withColumn("dia_semana", date_format("pickup_datetime", "EEEE"))
        
    kpi1_result = df_kpi1.groupBy("dia_semana", "franja_horaria").agg(
        count("*").alias("total_viajes"),
        avg("duration_mins").alias("duracion_promedio_mins"),
        avg("fare_amount").alias("tarifa_promedio")
    ).orderBy("dia_semana", "total_viajes", ascending=[True, False])
    
    kpi1_result.write.format("delta").mode("overwrite").saveAsTable("nyc_taxi_ivangalindo.refined.kpi1_demanda_temporal")
    
    # KPI 2: Eficiencia económica por zona [cite: 16]
    df_kpi2 = df.withColumn("ingreso_por_milla", col("fare_amount") / col("trip_distance")) \
                .withColumn("velocidad_promedio_mph", col("trip_distance") / (col("duration_mins") / 60))
                
    kpi2_result = df_kpi2.groupBy("pickup_borough", "pickup_zone").agg(
        avg("ingreso_por_milla").alias("ingreso_promedio_milla"),
        avg("velocidad_promedio_mph").alias("velocidad_promedio")
    ).orderBy(col("ingreso_promedio_milla").desc()).limit(10)
    
    kpi2_result.write.format("delta").mode("overwrite").saveAsTable("nyc_taxi_ivangalindo.refined.kpi2_top_10_zonas_rentables")
    
    logger.info("KPIs guardados en Unity Catalog exitosamente.")

if __name__ == "__main__":
    calculate_kpis()