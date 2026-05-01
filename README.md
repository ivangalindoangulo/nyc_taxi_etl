# nyc_taxi_etl
Pipeline ETL de NYC Yellow Taxi Trips

graph TD
    %% Fuentes de Datos
    Parquet[(Yellow Trips Parquet)]
    CSV[(Taxi Zones CSV)]

    %% Capa Raw
    subgraph Capa RAW
        RawTrips[(raw.yellow_trips)]
        RawZones[(raw.taxi_zones)]
    end

    %% Capa Trusted
    subgraph Capa TRUSTED
        TrustedTrips[(trusted.yellow_trips_enriched)]
    end

    %% Capa Refined
    subgraph Capa REFINED
        DQ[(refined.data_quality_report)]
        KPI1[(refined.kpi1_demanda_temporal)]
        KPI2[(refined.kpi2_top_10_zonas_rentables)]
    end

    %% Procesos
    Parquet -->|01_raw_ingestion| RawTrips
    CSV -->|01_raw_ingestion| RawZones
    
    RawTrips -->|02_trusted_processing| TrustedTrips
    RawZones -->|02_trusted_processing| TrustedTrips
    RawTrips -.->|Expectations Fail/Pass| DQ
    
    TrustedTrips -->|03_refined| KPI1
    TrustedTrips -->|03_refined| KPI2