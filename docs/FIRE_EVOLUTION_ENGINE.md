# IGNISPYRO / Flame Probabilistic Fire Evolution Engine

## Objective

Build a multi-fire, multi-area wildfire evolution engine capable of:

- reconstructing past fire spread from observations;
- generating time-stamped isochrones;
- estimating future spread probability;
- running for every active fire on the map or for a user-drawn area of interest;
- assimilating new satellite and operational observations continuously;
- exposing all workflows through the Flame domain-specific language (DSL), a Python API and a REST API.

The engine must never present a single deterministic perimeter as certainty. Every forecast product must include probability, uncertainty and provenance.

## Core principle

The system combines four complementary layers:

1. **Observed fire evidence** — MTG/FCI FRP, VIIRS, MODIS, Sentinel-3 SLSTR, operational perimeters and progression lines.
2. **Fuel potential** — NDMI, NDVI, NBR, land-cover/fuel models, fuel continuity and recent vegetation moisture anomaly.
3. **Physical spread constraints** — wind, slope, aspect, fuel model, dead/live fuel moisture and barriers.
4. **Probabilistic simulation and data assimilation** — ensemble spread simulation corrected whenever new observations arrive.

## Operational modes

### Mode A — All active fires

For every active fire:

- create an adaptive area of interest;
- assign satellite detections to the most plausible incident;
- reconstruct observed progression;
- run an ensemble forecast;
- publish probability rasters, forecast perimeters and isochrones.

### Mode B — Selected incident

The analyst selects one incident and can modify:

- ignition time and location;
- initial perimeter;
- forecast horizon;
- ensemble size;
- data sources;
- confidence thresholds;
- barriers and suppression actions.

### Mode C — User-defined area

The analyst draws a polygon and the engine evaluates:

- current active-fire evidence;
- fuel moisture and dryness potential;
- likely directions of spread if ignition occurs;
- conditional burn probability by forecast horizon.

This mode is a scenario assessment, not a declaration that a fire exists.

## Data sources

### Active fire and progression

- MTG FCI FRP pixel product;
- VIIRS 375 m active fire;
- MODIS active fire;
- Sentinel-3 SLSTR FRP;
- SGIF/VOST incident records;
- operational progression lines and perimeters;
- analyst-validated observations.

### Optical and thermal imagery

- Sentinel-2 Level-2A surface reflectance;
- Landsat 8/9 Collection 2 Level 2;
- optional commercial imagery adapters;
- pre-fire and post-fire composites.

### Atmospheric evidence

- CAMS aerosol optical depth;
- smoke/aerosol plume direction;
- optional Sentinel-5P aerosol products;
- wind-profile information for plume-consistency checks.

Aerosol information must be treated as supporting evidence. It must not be used as a direct fire-front location because smoke is transported away from the flaming front.

### Terrain, fuels and weather

- digital elevation model;
- slope and aspect;
- land cover and fuel model;
- roads, rivers, fuel breaks and non-burnable areas;
- IPMA observations and forecasts;
- ERA5/ERA5-Land for historical reconstruction;
- FWI components and fuel-moisture estimates.

## NDMI fuel-potential methodology

NDMI is calculated as:

```text
NDMI = (NIR - SWIR1) / (NIR + SWIR1)
```

Recommended bands:

- Sentinel-2: B8 and B11;
- Landsat 8/9: SR_B5 and SR_B6.

NDMI must not be used alone as spread probability. It becomes one feature in a calibrated fuel-potential model.

### Required NDMI products

1. most recent cloud-free NDMI;
2. 30-day median NDMI;
3. seasonal climatological NDMI;
4. NDMI anomaly relative to climatology;
5. temporal slope of NDMI over the previous weeks;
6. observation age and cloud-gap uncertainty.

### Fuel potential score

Initial formulation:

```text
fuel_potential = sigmoid(
    w1 * ndmi_anomaly_dry +
    w2 * ndmi_recent_decline +
    w3 * fuel_continuity +
    w4 * live_fuel_moisture_proxy +
    w5 * dead_fuel_moisture +
    w6 * drought_index
)
```

Weights must be learned and calibrated from historical fires. No fixed weight should be considered operationally valid before validation.

## Probabilistic evolution model

### Ensemble state

Each ensemble member contains:

- current perimeter;
- spread-rate correction factor;
- wind perturbation;
- fuel-moisture perturbation;
- spotting parameters;
- suppression/barrier effectiveness;
- uncertainty in ignition time and initial perimeter.

### Spread solver

Use a modular solver interface. Initial implementation should support:

- raster level-set or wavefront propagation;
- elliptical Huygens/Richards spread;
- optional adapters for external engines such as ForeFire, ELMFIRE, Cell2Fire or other validated models.

The native engine should be written in Python with performance-critical kernels implemented using NumPy/Numba initially, with a future Rust extension if profiling justifies it.

### Probability outputs

For each horizon, calculate:

- probability of arrival per cell;
- expected arrival time;
- 10th, 50th and 90th percentile arrival times;
- probability perimeter at 10%, 25%, 50%, 75% and 90%;
- ensemble median perimeter;
- uncertainty width;
- dominant spread direction;
- expected area and confidence interval.

## Observation assimilation

When a new fire observation arrives:

1. perform quality control;
2. assign it to an incident or mark it as unassigned;
3. compare it with each ensemble member;
4. reweight or resample members according to spatial and temporal agreement;
5. update the reconstructed perimeter;
6. restart the forecast from the corrected state.

Recommended first method: particle filtering, because fire perimeters are nonlinear and frequently non-Gaussian.

Observation likelihood should include:

- distance from observed point/polygon to simulated active edge;
- observation time difference;
- sensor positional uncertainty;
- cloud/visibility quality;
- FRP confidence;
- consistency with smoke direction;
- consistency with previous observations.

## Fire-to-detection association

For multiple simultaneous fires, use probabilistic incident association rather than nearest-point assignment.

Candidate score:

```text
association_score =
    spatial_continuity *
    temporal_continuity *
    predicted_reachability *
    wind_consistency *
    cluster_support *
    sensor_confidence
```

A detection remains unassigned when no incident exceeds the configured probability threshold.

## Reconstruction and isochrones

The engine produces:

- observed instantaneous thermal polygons;
- assimilated cumulative perimeter;
- hourly or configurable isochrones;
- uncertainty bands around each isochrone;
- source observations linked to each geometry;
- analyst-validated versions that remain immutable.

Every geometry must include:

- timestamp;
- incident identifier;
- source list;
- processing version;
- confidence score;
- model run identifier;
- validation status.

## Flame DSL design

Example:

```flame
area "Beira Baixa" from map

sources {
    fire: [MTG_FRP, VIIRS, SLSTR]
    imagery: [SENTINEL2, LANDSAT9]
    atmosphere: [CAMS_AOD]
    weather: IPMA
    terrain: COPERNICUS_DEM
    fuels: COS_FUEL_MODEL
}

fuel_potential {
    index NDMI
    baseline seasonal_climatology years 5
    anomaly true
    max_image_age 10 days
}

simulate fires active within area {
    horizon 24 hours
    timestep 10 minutes
    ensemble 500
    solver "levelset"
    assimilate every 10 minutes
    output probability [0.10, 0.25, 0.50, 0.75, 0.90]
    output isochrones every 1 hour
}

publish to "IGNISPYRO:8097"
```

Area-specific scenario:

```flame
area "scenario" draw polygon

scenario ignition at map.center time now {
    horizon 12 hours
    ensemble 1000
    use NDMI latest
    use wind forecast
    output arrival_probability
}
```

## Repository architecture

```text
flame-lang/
├── flame/
│   ├── parser/
│   ├── ast/
│   ├── runtime/
│   └── wildfire/
│       ├── commands.py
│       └── schema.py
├── fire_engine/
│   ├── domain/
│   ├── ingestion/
│   │   ├── mtg.py
│   │   ├── firms.py
│   │   ├── sentinel.py
│   │   ├── landsat.py
│   │   └── cams.py
│   ├── fuels/
│   │   ├── ndmi.py
│   │   ├── climatology.py
│   │   └── fuel_potential.py
│   ├── association/
│   ├── reconstruction/
│   ├── spread/
│   ├── assimilation/
│   ├── probability/
│   ├── validation/
│   └── api/
├── gee/
│   ├── ndmi_sentinel2.js
│   ├── ndmi_landsat.js
│   └── export_fuel_potential.js
├── db/
│   ├── migrations/
│   └── postgis/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── historical_fires/
└── docs/
```

## Technology stack

- Python 3.12;
- FastAPI and Pydantic;
- PostgreSQL/PostGIS;
- GeoPandas, Shapely, Rasterio, Xarray and rioxarray;
- NumPy, SciPy and Numba;
- Dask for large historical processing;
- Celery or Dramatiq with Redis for jobs;
- Google Earth Engine Python API for imagery preprocessing;
- MLflow for experiment tracking;
- PyTorch or scikit-learn for calibrated probability models;
- Docker Compose for development;
- GitHub Actions for linting, tests, security checks and container builds.

## API products

Suggested endpoints:

```text
POST /areas
POST /incidents/{id}/reconstruct
POST /incidents/{id}/forecast
POST /areas/{id}/scenario
GET  /runs/{id}
GET  /runs/{id}/probability
GET  /runs/{id}/isochrones
GET  /runs/{id}/observations
POST /runs/{id}/validate
```

## Validation strategy

Start with historical fires with reliable progression data, including the cases identified by the project owner.

For each fire, calculate:

- Intersection over Union of forecast and observed perimeters;
- Hausdorff and mean boundary distance;
- arrival-time MAE;
- Brier score for probability of arrival;
- reliability diagrams;
- probability calibration error;
- area error by horizon;
- false-association rate for satellite detections.

Use spatially and temporally separated train, validation and test fires. Never validate on the same incidents used to tune the model.

## Quality and safety rules

- Always label outputs as observed, reconstructed, simulated or analyst-validated.
- Never overwrite raw observations.
- Store model version and configuration with every run.
- Include observation age and missing-data flags.
- Do not infer a fire front from aerosol data alone.
- Do not treat NDMI as a direct rate-of-spread model.
- Provide deterministic fallbacks when probabilistic dependencies fail.
- Every operational map must display timestamp and uncertainty.

## Delivery phases

### Phase 1 — Foundation

- data schemas;
- PostGIS migrations;
- MTG ingestion;
- incident association;
- observed isochrones;
- Flame syntax for sources, areas and outputs.

### Phase 2 — Fuel potential

- GEE Sentinel-2 and Landsat NDMI pipelines;
- cloud masking and compositing;
- NDMI anomaly and image-age uncertainty;
- fuel-potential raster service.

### Phase 3 — Native spread engine

- terrain/fuel/weather raster preparation;
- ensemble spread solver;
- probability and arrival-time products;
- API and map integration.

### Phase 4 — Assimilation

- particle filter;
- continuous correction using MTG/VIIRS/perimeters;
- multi-fire association;
- automatic reruns.

### Phase 5 — Scientific validation

- historical-fire benchmark suite;
- calibration reports;
- reproducible experiments;
- publication-ready methodology.

## Definition of success

The system is ready for operational trials only when it can:

1. process multiple simultaneous fires without mixing detections;
2. reconstruct hourly isochrones with provenance;
3. produce calibrated probability maps;
4. update forecasts automatically after new observations;
5. quantify uncertainty and observation age;
6. reproduce benchmark runs from versioned inputs and configuration;
7. run on the existing QNAP/PostGIS/FastAPI infrastructure with heavier processing delegated to an optional worker machine.
