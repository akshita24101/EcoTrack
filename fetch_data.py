from db_connect import get_db

db = get_db()

print("\n----- SITES -----")
for site in db.sites.find():
    print(site)

print("\n----- ASSETS -----")
for asset in db.assets.find():
    print(asset)

print("\n----- TELEMETRY -----")
for t in db.telemetry.find():
    print(t)

print("\n----- ALERTS -----")
for alert in db.alerts.find():
    print(alert)
