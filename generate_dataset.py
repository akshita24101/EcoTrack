import json, csv, random
from datetime import datetime, timedelta

# ---------- OUTPUT FILES ----------
SITES_FILE = "sites.json"
ASSETS_FILE = "assets.json"
TELEMETRY_FILE = "telemetry.csv"
WASTE_FILE = "waste_logs.csv"
SP_FILE = "service_providers.json"
ALERTS_FILE = "alerts.json"

# ---------- SITES ----------
sites = [
    {"site_id": 1, "name": "Raipur Plant", "location": {"type":"Point","coordinates":[81.6296,21.2514]}},
    {"site_id": 2, "name": "Bhilai Warehouse", "location": {"type":"Point","coordinates":[81.4318,21.193]}},
]

with open(SITES_FILE, "w") as f:
    json.dump(sites, f, indent=2)

# ---------- ASSETS ----------
assets = [
    {"asset_id": 101, "site_id": 1, "type": "electricity_meter", "name": "Main Meter A"},
    {"asset_id": 102, "site_id": 1, "type": "machine", "name": "Machine A"},
    {"asset_id": 103, "site_id": 1, "type": "compressor", "name": "Compressor A"},
    {"asset_id": 201, "site_id": 2, "type": "electricity_meter", "name": "Warehouse Meter"},
    {"asset_id": 202, "site_id": 2, "type": "forklift", "name": "EV Forklift"},
    {"asset_id": 203, "site_id": 2, "type": "solar_panel", "name": "Solar Panel Roof"}
]

with open(ASSETS_FILE, "w") as f:
    json.dump(assets, f, indent=2)

# ---------- TELEMETRY (1 YEAR HOURLY ≈ 52,560 ROWS) ----------
start = datetime(2024,1,1,0,0,0)
end = datetime(2024,12,31,23,0,0)

hours = int((end - start).total_seconds()/3600)
rows = []

current = start

while current <= end:
    for a in assets:
        base = {
            "electricity_meter": 20,
            "machine": 8,
            "compressor": 6,
            "solar_panel": 3,
            "forklift": 5
        }.get(a["type"], 6)

        # realistic variations
        value = round(base + random.uniform(-2, 3), 2)

        rows.append([
            current.isoformat(),
            a["asset_id"],
            a["site_id"],
            "electricity_kWh",
            value
        ])

    current += timedelta(hours=1)

with open(TELEMETRY_FILE, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["timestamp","asset_id","site_id","value_type","value"])
    writer.writerows(rows)

# ---------- WASTE LOGS ----------
waste = []
waste_types = ["plastic","metal","organic","hazardous"]

d = datetime(2024,1,1)
for i in range(365):
    waste.append({
        "site_id": 1,
        "date": d.strftime("%Y-%m-%d"),
        "type": random.choice(waste_types),
        "quantity_kg": round(random.uniform(50,200),2)
    })
    d += timedelta(days=1)

with open(WASTE_FILE, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=waste[0].keys())
    writer.writeheader()
    writer.writerows(waste)

# ---------- SERVICE PROVIDERS ----------
providers = [
    {"name": "Raipur Recycling Center", "location": {"type": "Point","coordinates":[81.63,21.25]}},
    {"name": "Bhilai Solar Services", "location": {"type": "Point","coordinates":[81.43,21.19]}},
]

with open(SP_FILE, "w") as f:
    json.dump(providers, f, indent=2)

# ---------- ALERTS ----------
alerts = []
for i in range(50):
    alerts.append({
        "alert_id": 8000+i,
        "asset_id": random.choice([101,102,103,201,202]),
        "timestamp": datetime(2024, random.randint(1,12), random.randint(1,28)).isoformat(),
        "alert_type": "anomaly",
        "value": round(random.uniform(30,50),2)
    })

with open(ALERTS_FILE, "w") as f:
    json.dump(alerts, f, indent=2)

print("DATASET GENERATED SUCCESSFULLY!")
