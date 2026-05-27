DATA_PATH = "data/owid-co2-data.csv"

MODEL_PATH = "models/best_model.pkl"
MODEL_METADATA_PATH = "models/model_metadata.pkl"

STYLE_PATH = "assets/styles/main.css"
JS_PATH = "assets/js/main.js"

PAGE_TITLE = "CO₂ 배출량 분석 대시보드"
PAGE_ICON = "🌍"

FEATURES = [
    "year",
    "population",
    "gdp",
    "primary_energy_consumption",
    "energy_per_capita"
]

TARGET = "co2"

IMPORTANT_COLUMNS = [
    "country",
    "year",
    "iso_code",
    "population",
    "gdp",
    "co2",
    "co2_per_capita",
    "primary_energy_consumption",
    "energy_per_capita",
    "coal_co2",
    "oil_co2",
    "gas_co2",
    "cement_co2"
]