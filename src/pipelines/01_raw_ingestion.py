import sys
import os

# Ruta
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '../..')))

import urllib.request
import time
import argparse
from pyspark.sql import SparkSession
from src.utils.logger import get_logger, ExecutionReport


# 1. Inicialización y captura de variables
spark = SparkSession.builder.appName("RawIngestion").getOrCreate()
logger = get_logger()
report = ExecutionReport()

parser = argparse.ArgumentParser()
parser.add_argument("--catalog", required=True, help="Nombre del catálogo de Unity Catalog")
args = parser.parse_args()
CATALOG_NAME = args.catalog

URLS = {
    "yellow_trips": "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-01.parquet",
    "taxi_zones": "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"
}

def process_raw():
    start_time = time.time()
    logger.info(f"Configurando Gobierno de Datos en el catálogo: {CATALOG_NAME}...")

    # 2. Crear esquemas y el Volumen de aterrizaje
    spark.sql(f"USE CATALOG {CATALOG_NAME}")
    spark.sql("CREATE SCHEMA IF NOT EXISTS raw")
    spark.sql("CREATE SCHEMA IF NOT EXISTS trusted")
    spark.sql("CREATE SCHEMA IF NOT EXISTS refined")
    spark.sql("CREATE VOLUME IF NOT EXISTS raw.landing")

    # 3. Descarga de datos fuente al Volumen de Unity Catalog
    volume_path = f"/Volumes/{CATALOG_NAME}/raw/landing/"
    logger.info(f"Iniciando descarga de datos en: {volume_path}")

    downloaded_paths = {}
    for name, url in URLS.items():
        file_name = url.split("/")[-1]
        full_dest = os.path.join(volume_path, file_name)
        logger.info(f"Descargando {name} desde {url}...")
        try:
            urllib.request.urlretrieve(url, full_dest)
            downloaded_paths[name] = full_dest
            logger.info(f"Éxito: Guardado en {full_dest}")
        except Exception as e:
            logger.error(f"Error en descarga de {name}: {str(e)}")
            raise e

    # 4. Lectura y Escritura a Tablas Delta
    logger.info("Iniciando carga a tablas Delta (Capa RAW)...")
    
    df_trips = spark.read.parquet(downloaded_paths["yellow_trips"])
    df_zones = spark.read.option("header", "true").csv(downloaded_paths["taxi_zones"])
    
    df_trips.write.format("delta").mode("overwrite").saveAsTable(f"{CATALOG_NAME}.raw.yellow_trips")
    df_zones.write.format("delta").mode("overwrite").saveAsTable(f"{CATALOG_NAME}.raw.taxi_zones")
    
    logger.info("Ingesta capa RAW completada exitosamente.")
    report.add_stage("RAW_INGESTION", time.time() - start_time, df_trips.count(), df_trips.count())

if __name__ == "__main__":
    process_raw()