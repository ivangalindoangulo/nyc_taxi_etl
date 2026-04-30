import urllib.request
import os

# Definición de URLs y rutas (Senior Tip: Centraliza tus constantes) [cite: 483]
URLS = {
    "yellow_trips": "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-01.parquet",
    "taxi_zones": "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"
}

# Ruta en tu Volume de Unity Catalog [cite: 495, 636]
DEST_PATH = "/Volumes/nyc_taxi_ivangalindo/raw/landing/"

def download_files():
    print(f"Iniciando descarga de datos fuente en: {DEST_PATH}")
    
    # Crear el directorio si no existe
    os.makedirs(DEST_PATH, exist_ok=True)
    
    for name, url in URLS.items():
        file_name = url.split("/")[-1]
        full_dest = os.path.join(DEST_PATH, file_name)
        
        print(f"Descargando {name} desde {url}...")
        try:
            urllib.request.urlretrieve(url, full_dest)
            print(f"Éxito: Guardado en {full_dest}")
        except Exception as e:
            print(f"Error: descarga {name}: {str(e)}")
            raise e

if __name__ == "__main__":
    download_files()