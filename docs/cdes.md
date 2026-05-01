# Critical Data Elements (CDEs) - NYC Taxi Pipeline

Este documento define los Elementos Críticos de Datos fundamentales para asegurar la confiabilidad de los KPIs de negocio.

| CDE Name | Definición de Negocio | Regla de Calidad (Data Quality Rule) | Tabla y Columna (Origen) |
| :--- | :--- | :--- | :--- |
| **Duración del Viaje** | El tiempo transcurrido entre la recogida y la bajada del pasajero. Crucial para calcular métricas de eficiencia y velocidad. | `tpep_dropoff_datetime` debe ser estrictamente mayor a `tpep_pickup_datetime`. No se admiten duraciones negativas o en cero. | `raw.yellow_trips` <br> (`tpep_pickup_datetime`, `tpep_dropoff_datetime`) |
| **Distancia Recorrida** | La distancia física del viaje reportada por el taxímetro. Indispensable para el cálculo del ingreso por milla. | `trip_distance` > 0. El viaje debe tener una distancia comprobable para ser monetizado. | `raw.yellow_trips` <br> (`trip_distance`) |
| **Tarifa Base** | El monto económico cobrado por el viaje, excluyendo propinas y peajes. Base para cálculos de rentabilidad. | `fare_amount` > 0. Se descartan viajes gratuitos o con errores de cobro (valores negativos). | `raw.yellow_trips` <br> (`fare_amount`) |