import logging
import json
import time

def get_logger(name="NYCTaxiETL"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        ch = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    return logger

class ExecutionReport:
    def __init__(self):
        self.report = {"etapas": {}, "resumen": {}}
        
    def add_stage(self, stage_name, time_taken, total_read, total_written, discarded=0):
        self.report["etapas"][stage_name] = {
            "tiempo_segundos": round(time_taken, 2),
            "registros_leidos": total_read,
            "registros_escritos": total_written,
            "descartados": discarded
        }
        
    def save(self, path="execution_report.json"):
        with open(path, "w") as f:
            json.dump(self.report, f, indent=4)