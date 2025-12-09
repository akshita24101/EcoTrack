# dashboard.py
# Streamlit dashboard for EcoTrack-Enterprise (MongoDB backend)
# Put this file in your project folder and run: streamlit run dashboard.py

import streamlit as st
from pymongo import MongoClient
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# Try to import prophet optionally
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except Exception:
    PROPHET_AVAILABLE = False

st.set_page_config(page_title="EcoTrack Enterprise", layout="wide")

# ------------------------
# Helper: DB connection
# ------------------------
@st.cache_resource
def get_db():
    client = MongoClient("mongodb://localhost:27017/")
    return client["ecotrack"]

db = get_db()

# ------------------------
# Utility functions
# ------------------------
def create_2dsphere_index():
    """Create 2dsphere index on service_providers.location if not exists."""
    coll = db.service_providers
    # check existing indexes quickly
    indexes = coll.index_information()
    for name, info in indexes.items():
        keys = info.get("key", [])
        for key in keys:
            if key[0] == "location":
                return "2dsphere index already exists"
    coll.create_index([("location", "2dsphere")])
    return "2dsphere index created"

def load_sites():
    sites = list(db.sites.find({}, {"_id": 0, "site_id": 1, "name": 1}))
    if not sites:
        return []
    return sites

def telemetry_df(site_id=None, start=None, end=None):
    """
    Returns telemetry as pandas DataFrame filtered by site_id and date range.
    Assumes telemetry documents have timestamp (ISO string), asset_id, value_type, value.
    """
    q = {}
    if site_id and site_id != "All":
        # first find asset_ids for site
        asset_ids = [a["asset_id"] for a in db.assets.find({"site_id": site_id}, {"asset_id": 1})]
        q["asset_id"] = {"$in": asset_ids} if asset_ids else {"$exists": False}
    if start or end:
        # convert to strings in ISO if needed
        q["timestamp"] = {}
        if start:
            q["timestamp"]["$gte"] = start.strftime("%Y-%m-%dT%H:%M:%S")
        if end:
            q["timestamp"]["$lte"] = end.strftime("%Y-%m-%dT%H:%M:%S")
        if not q["timestamp"]:
            q.pop("timestamp")

    cursor = db.telemetry.find(q)
    rows = list(cursor)
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    # ensure timestamp is datetime
    if "timestamp" in df.columns:
        try:
            df["ts"] = pd.to_datetime(df["timestamp"])
        except Exception:
            # if already datetime-like, keep
            df["ts"] = pd.to_datetime(df["timestamp"], errors="coerce")
    else:
        df["ts"] = pd.NaT
    return df

def calc_total_kwh(df):
    if df.empty:
        return 0.0
    return float(df[df["value_type"] == "electricity_kWh"]["value"].sum())

def calc_emissions_kg(total_kwh, factor=0.82):
    return total_kwh * factor

def daily_aggregates(df):
    if df.empty:
        return pd.DataFrame(columns=["date", "daily_kWh"])
    d = df[df["value_type"] == "electricity_kWh"].copy()
    d["date"] = d["ts"].dt.date
    agg = d.groupby("date")["value"].sum().reset_index().rename(columns={"value": "daily_kWh"})
    agg["date"] = pd.to_datetime(agg["date"])
    return agg.sort_values("date")

def asset_aggregates(df):
    if df.empty:
        return pd.DataFrame(columns=["asset_id", "total_kWh"])
    d = df[df["value_type"] == "electricity_kWh"].copy()
    agg = d.groupby("asset_id")["value"].sum().reset_index().rename(columns={"value": "total_kWh"})
    return agg.sort_values("total_kWh", ascending=False)

def simple_moving_average_forecast(series, days_out=7, window=3):
    # series: pandas Series indexed by date
    if series.empty:
        return pd.Series(dtype=float)
    ma = series.rolling(window=window, min_periods=1).mean()
    last = ma.iloc[-1]
    # naive forecast: repeat last moving average for next days
    future_idx = pd.date_range(start=series.index[-1] + pd.Timedelta(days=1), periods=days_out)
    return pd.Series([last]*days_out, index=future_idx)

def prophet_forecast(series, days_out=14):
    """Run Prophet if available. Input: series indexed by date (pd.Series)."""
    if not PROPHET_AVAILABLE:
        raise RuntimeError("Prophet not available")
    df = series.reset_index().rename(columns={"index": "ds", 0: "y"})
    m = Prophet(daily_seasonality=True)
    m.fit(df)
    future = m.make_future_dataframe(periods=days_out)
    forecast = m.predict(future)
    # return forecast for last days_out
    return forecast[["ds", "yhat"]].set_index("ds")["yhat"].iloc[-days_out:]

# ------------------------
# Streamlit UI
# ------------------------
st.title("EcoTrack — Enterprise Sustainability Dashboard")
st.markdown("MongoDB + Streamlit demo for EcoTrack-Enterprise. 💚")

# Left pane: filters
with st.sidebar:
    st.header("Filters")
    sites = load_sites()
    site_options = ["All"] + [s["name"] for s in sites]
    chosen_site_name = st.selectbox("Select Site", site_options)
    # map site name to site_id
    site_map = {s["name"]: s["site_id"] for s in sites}
    chosen_site_id = site_map.get(chosen_site_name, "All")

    today = datetime.now()
    default_start = today - timedelta(days=14)
    start_date = st.date_input("Start date", default_start)
    end_date = st.date_input("End date", today)
    st.write(" ")
    st.subheader("Geo / Index")
    if st.button("Create 2dsphere index on service_providers"):
        msg = create_2dsphere_index()
        st.success(msg)

    st.write(" ")
    st.markdown("---")
    st.markdown("Forecasting")
    use_prophet = False
    if PROPHET_AVAILABLE:
        use_prophet = st.checkbox("Use Prophet for forecast (optional)", value=False)
    else:
        st.info("Prophet not installed — moving average forecast will be used. (optional)")

# Load telemetry per filters
start_dt = datetime.combine(start_date, datetime.min.time())
end_dt = datetime.combine(end_date, datetime.max.time())
df = telemetry_df(site_id=chosen_site_id if chosen_site_id!="All" else None, start=start_dt, end=end_dt)

# Top KPIs
col1, col2, col3, col4 = st.columns(4)
total_kwh = calc_total_kwh(df)
emissions = calc_emissions_kg(total_kwh)
avg_kwh = 0.0
if not df.empty:
    avg_kwh = float(df[df["value_type"]=="electricity_kWh"]["value"].mean())

col1.metric("Total electricity (kWh)", f"{total_kwh:.2f}")
col2.metric("Total emissions (kg CO₂)", f"{emissions:.2f}")
col3.metric("Average reading (kWh)", f"{avg_kwh:.2f}")
col4.metric("Telemetry points", len(df))

st.markdown("---")

# Charts area
left, right = st.columns([2,1])

with left:
    st.subheader("Daily Electricity Usage")
    daily = daily_aggregates(df)
    if daily.empty:
        st.info("No electricity telemetry found for the selected filters.")
    else:
        # line chart
        chart_df = daily.set_index("date")["daily_kWh"]
        st.line_chart(chart_df)

    st.subheader("Asset-wise Usage (Top 10)")
    asset_df = asset_aggregates(df)
    if asset_df.empty:
        st.info("No asset data")
    else:
        top10 = asset_df.head(10).set_index("asset_id")["total_kWh"]
        st.bar_chart(top10)

    st.subheader("Highest Spikes / Anomalies (Simple)")
    if df.empty:
        st.write("No data to analyze anomalies.")
    else:
        # simple z-score anomaly detection per asset
        from sklearn.preprocessing import StandardScaler
        z_df = df[df["value_type"]=="electricity_kWh"].copy()
        if z_df.empty:
            st.write("No electricity data")
        else:
            grouped = z_df.groupby("asset_id")
            anomaly_records = []
            for aid, g in grouped:
                arr = g["value"].values
                if len(arr) < 2:
                    continue
                mean = arr.mean()
                std = arr.std(ddof=0) if arr.std(ddof=0) > 0 else 1.0
                # mark datapoints with z > 2.5
                mask = (g["value"] - mean) / std > 2.5
                for idx, val in g[mask].iterrows():
                    anomaly_records.append({
                        "asset_id": aid,
                        "timestamp": val["timestamp"],
                        "value": val["value"],
                        "z": (val["value"]-mean)/std
                    })
            if anomaly_records:
                st.table(pd.DataFrame(anomaly_records))
            else:
                st.write("No strong anomalies detected (z>2.5).")

with right:
    st.subheader("Forecast")
    # Prepare series for forecasting
    if daily.empty:
        st.info("No daily series available for forecasting.")
    else:
        series = daily.set_index("date")["daily_kWh"].copy()
        # make sure index is datetime and sorted
        series.index = pd.to_datetime(series.index)
        series = series.sort_index()
        days_out = st.number_input("Forecast horizon (days)", min_value=1, max_value=90, value=14)
        if PROPHET_AVAILABLE and use_prophet:
            try:
                with st.spinner("Running Prophet..."):
                    forecast_series = prophet_forecast(series, days_out=days_out)
                    last_index = series.index[-1]
                    # plot combined
                    combined = pd.concat([series, forecast_series.rename("yhat")])
                    fig, ax = plt.subplots(figsize=(6,3))
                    ax.plot(series.index, series.values, label="Actual")
                    ax.plot(forecast_series.index, forecast_series.values, label="Prophet Forecast")
                    ax.legend()
                    ax.set_xlabel("Date")
                    ax.set_ylabel("kWh")
                    st.pyplot(fig)
            except Exception as e:
                st.error("Prophet error: " + str(e))
        else:
            # moving average forecast
            wa = simple_moving_average_forecast(series, days_out=days_out, window=3)
            fig, ax = plt.subplots(figsize=(6,3))
            ax.plot(series.index, series.values, label="Actual")
            ax.plot(wa.index, wa.values, label=f"{len(wa)}-day MA Forecast")
            ax.legend()
            ax.set_xlabel("Date")
            ax.set_ylabel("kWh")
            st.pyplot(fig)

    st.subheader("Nearest Service Providers (Map)")
    # Map of service providers
    provs = list(db.service_providers.find({}, {"_id":0, "name":1, "type":1, "location":1}))
    if not provs:
        st.info("No service providers found in DB.")
    else:
        rows = []
        for p in provs:
            loc = p.get("location", {})
            coords = loc.get("coordinates") if loc else None
            if coords and isinstance(coords, list) and len(coords) >= 2:
                # streamlit map expects [lat, lon] in dataframe
                rows.append({"name": p.get("name", ""), "type": p.get("type",""), "lat": coords[1], "lon": coords[0]})
        if rows:
            prov_df = pd.DataFrame(rows)
            st.map(prov_df.rename(columns={"lat":"lat","lon":"lon"})[["lat","lon"]])
            st.table(prov_df[["name","type"]].head(10))
        else:
            st.info("Service provider locations invalid or missing coordinates.")

st.markdown("---")
st.caption("Built for EcoTrack-Enterprise — MongoDB based sustainability intelligence demo.")
