# -----------------------------------------------------
#  aggregation_queries.py
#  This file contains all MongoDB Aggregation Pipelines
#  for your EcoTrack project.
# -----------------------------------------------------

from db_connect import get_db

# Connect to database
db = get_db()


# -----------------------------------------------------
# 1️⃣ TOTAL ELECTRICITY CONSUMPTION
# -----------------------------------------------------
print("\n1️⃣ Total Electricity Consumption (kWh):")

pipeline_total = [
    {"$match": {"value_type": "electricity_kWh"}},     # Filter only electricity readings
    {"$group": {
        "_id": None,
        "total_kWh": {"$sum": "$value"}               # Sum all values
    }}
]

result_total = list(db.telemetry.aggregate(pipeline_total))
print(result_total)



# -----------------------------------------------------
# 2️⃣ ELECTRICITY USAGE PER ASSET (PER MACHINE)
# -----------------------------------------------------
print("\n2️⃣ Electricity Usage Per Asset:")

pipeline_asset = [
    {"$match": {"value_type": "electricity_kWh"}},
    {"$group": {
        "_id": "$asset_id",                           # Group by each machine
        "total_kWh": {"$sum": "$value"}
    }}
]

result_asset = list(db.telemetry.aggregate(pipeline_asset))
print(result_asset)



# -----------------------------------------------------
# 3️⃣ AVERAGE ELECTRICITY USAGE
# -----------------------------------------------------
print("\n3️⃣ Average Electricity Usage (kWh):")

pipeline_avg = [
    {"$match": {"value_type": "electricity_kWh"}},
    {"$group": {
        "_id": None,
        "average_kWh": {"$avg": "$value"}             # Calculate average
    }}
]

result_avg = list(db.telemetry.aggregate(pipeline_avg))
print(result_avg)



# -----------------------------------------------------
# 4️⃣ DAILY ELECTRICITY USAGE
# -----------------------------------------------------
print("\n4️⃣ Electricity Usage Per Day:")

pipeline_daily = [
    {"$match": {"value_type": "electricity_kWh"}},
    {"$group": {
        "_id": {"$substr": ["$timestamp", 0, 10]},    # Extract date from timestamp
        "daily_kWh": {"$sum": "$value"}               # Sum values per date
    }},
    {"$sort": {"_id": 1}}                             # Sort by date
]

result_daily = list(db.telemetry.aggregate(pipeline_daily))
print(result_daily)



# -----------------------------------------------------
# 5️⃣ HIGHEST ELECTRICITY SPIKE (MAX USAGE)
# -----------------------------------------------------
print("\n5️⃣ Highest Electricity Spike:")

pipeline_spike = [
    {"$match": {"value_type": "electricity_kWh"}},
    {"$sort": {"value": -1}},                         # Sort highest first
    {"$limit": 1}                                     # Take only top 1
]

result_spike = list(db.telemetry.aggregate(pipeline_spike))
print(result_spike)



# -----------------------------------------------------
# 6️⃣ EMISSION CALCULATION (CARBON FOOTPRINT)
# -----------------------------------------------------
print("\n6️⃣ Total Emissions (kg CO₂):")
# 1 kWh = 0.82 kg CO₂ (emission factor)

pipeline_emission = [
    {"$match": {"value_type": "electricity_kWh"}},
    {"$group": {
        "_id": None,
        "total_kgCO2": {"$sum": {"$multiply": ["$value", 0.82]}}
    }}
]

result_emission = list(db.telemetry.aggregate(pipeline_emission))
print(result_emission)



# -----------------------------------------------------
# 7️⃣ GEONEAR — NEAREST RECYCLING CENTER
# -----------------------------------------------------
print("\n7️⃣ Nearest Recycling / Service Provider:")

pipeline_geo = [
    {
        "$geoNear": {
            "near": {"type": "Point", "coordinates": [81.6296, 21.2514]},  # Your site's location
            "distanceField": "distance",
            "spherical": True
        }
    }
]

# NOTE: To run this query, ensure 2dsphere index is created on service_providers.location

try:
    result_geo = list(db.service_providers.aggregate(pipeline_geo))
    print(result_geo)
except Exception as e:
    print("GeoNear requires 2dsphere index!")
    print("Error:", e)
