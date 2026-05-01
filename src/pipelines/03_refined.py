import sys
import os

# Ruta
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '../..')))

import json
import datetime
import argparse
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, hour, date_format, avg, count, unix_timestamp, when
from src.utils.logger import get_logger



# 1. Inicializar Spark y variables
spark = SparkSession.builder.appName("RefinedProcessing").getOrCreate()
logger = get_logger()

parser = argparse.ArgumentParser()
parser.add_argument("--catalog", required=True, help="Nombre del catálogo")
args = parser.parse_args()
CATALOG_NAME = args.catalog

def calculate_kpis():
    logger.info("Calculando KPIs OBLIGATORIOS (Refined)...")
    
    # 2. Uso dinámico del catálogo
    df = spark.table(f"{CATALOG_NAME}.trusted.yellow_trips_enriched")
    
    df = df.withColumn("duration_mins", 
        (unix_timestamp("dropoff_datetime") - unix_timestamp("pickup_datetime")) / 60)
        
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
    
    kpi1_result.write.format("delta").mode("overwrite").saveAsTable(f"{CATALOG_NAME}.refined.kpi1_demanda_temporal")
    
    df_kpi2 = df.withColumn("ingreso_por_milla", col("fare_amount") / col("trip_distance")) \
                .withColumn("velocidad_promedio_mph", col("trip_distance") / (col("duration_mins") / 60))
                
    kpi2_result = df_kpi2.groupBy("pickup_borough", "pickup_zone").agg(
        avg("ingreso_por_milla").alias("ingreso_promedio_milla"),
        avg("velocidad_promedio_mph").alias("velocidad_promedio")
    ).orderBy(col("ingreso_promedio_milla").desc()).limit(10)
    
    kpi2_result.write.format("delta").mode("overwrite").saveAsTable(f"{CATALOG_NAME}.refined.kpi2_top_10_zonas_rentables")
    
    logger.info("KPIs guardados en Unity Catalog exitosamente.")


def generate_json_report():
    logger.info("Generando reporte de ejecución final en JSON...")
    
    # Extraer métricas consultando las tablas
    total_raw = spark.table(f"{CATALOG_NAME}.raw.yellow_trips").count()
    
    try:
        df_dq = spark.table(f"{CATALOG_NAME}.refined.data_quality_report")
        descartados = df_dq.filter(col("is_valid") == False).select("count").collect()[0][0]
    except Exception:
        descartados = 0
        
    total_procesado = total_raw - descartados
    
    # Estructurar el JSON
    report_data = {
        "pipeline_name": "nyc_taxi_etl",
        "execution_timestamp": str(datetime.datetime.now()),
        "status": "SUCCESS",
        "metrics": {
            "1_registros_crudos_leidos": total_raw,
            "2_registros_anomalos_descartados": descartados,
            "3_registros_validos_procesados": total_procesado
        },
        "kpis_generados": [
            f"{CATALOG_NAME}.refined.kpi1_demanda_temporal",
            f"{CATALOG_NAME}.refined.kpi2_top_10_zonas_rentables"
        ]
    }
    
    # Guardar el JSON en el volumen de Unity Catalog
    report_path = f"/Volumes/{CATALOG_NAME}/raw/landing/execution_report.json"
    
    with open(report_path, "w") as f:
        json.dump(report_data, f, indent=4)
        
    logger.info(f"✅ Reporte JSON guardado exitosamente en: {report_path}")
    
    print("\n--- REPORTE FINAL DE EJECUCIÓN ---")
    print(json.dumps(report_data, indent=4))
    print("----------------------------------\n")

if __name__ == "__main__":
    calculate_kpis()
    generate_json_report()