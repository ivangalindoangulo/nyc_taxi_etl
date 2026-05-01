# Glosario de Negocio - NYC Taxi

| Término | Definición |
| :--- | :--- |
| **Viaje Válido** | Aquel registro de viaje que supera exitosamente todas las validaciones de calidad de datos (CDEs), incluyendo distancias y tarifas positivas, y coherencia temporal. |
| **Franja Horaria** | Agrupación lógica de las horas del día para analizar patrones de demanda. Se divide en: Madrugada (0-3h), Mañana Temprano (4-7h), Mañana (8-11h), Tarde (12-15h), Noche (16-19h) y Noche Tardía (20-23h). |
| **Borough** | Cada uno de los distritos principales o divisiones administrativas de la ciudad de Nueva York (ej. Manhattan, Queens, Brooklyn) donde inician o terminan los viajes. |
| **Ingreso por Milla** | KPI de eficiencia económica que calcula la rentabilidad de un viaje dividiendo el costo total de la tarifa base (`fare_amount`) entre la distancia recorrida (`trip_distance`). |
| **Data Quality Report** | Tabla de auditoría en la capa Refined que cuantifica el volumen de datos íntegros frente a los datos anómalos interceptados por las barreras de calidad (Expectations). |