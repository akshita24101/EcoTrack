# EcoTrack Enterprise
**Environmental Monitoring & Sustainability Analytics Platform**

EcoTrack is a comprehensive environmental monitoring system designed for enterprise-level sustainability tracking. It provides real-time monitoring of energy consumption, waste management, carbon footprint calculation, and environmental compliance analytics.

## 🌍 Features

- **Real-time Energy Monitoring**: Track electricity consumption across multiple sites and assets
- **Carbon Footprint Analytics**: Calculate and monitor CO₂ emissions with industry-standard factors
- **Waste Management Tracking**: Monitor and analyze waste generation and disposal patterns
- **Geospatial Services**: Find nearest recycling centers and service providers
- **Interactive Dashboard**: Streamlit-based web interface for data visualization
- **Predictive Analytics**: Future consumption forecasting (Prophet integration)
- **MongoDB Backend**: Scalable NoSQL database for time-series data storage

## 🏗️ Architecture

```
EcoTrack/
├── dashboard.py              # Streamlit web dashboard
├── db_connect.py            # MongoDB connection utilities
├── aggregation_queries.py   # MongoDB aggregation pipelines
├── generate_dataset.py      # Synthetic data generation
├── fetch_data.py           # Data ingestion utilities
├── sites.json              # Site configuration data
├── assets.json             # Asset/equipment definitions
├── service_providers.json  # Service provider locations
├── alerts.json            # Alert configuration
├── telemetry.csv          # Time-series telemetry data
└── waste_logs.csv         # Waste tracking records
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MongoDB 4.4+
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/[username]/ecotrack-enterprise.git
cd ecotrack-enterprise
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Start MongoDB**
```bash
# Windows
net start MongoDB

# macOS/Linux
sudo systemctl start mongod
```

4. **Import sample data**
```bash
python generate_dataset.py
python fetch_data.py
```

5. **Launch the dashboard**
```bash
streamlit run dashboard.py
```

## 📊 Dashboard Features

### Main Analytics
- **Energy Consumption Overview**: Total and per-asset electricity usage
- **Daily/Weekly/Monthly Trends**: Time-series analysis with interactive charts
- **Carbon Footprint Tracking**: Real-time CO₂ emissions calculation
- **Peak Usage Identification**: Identify energy spikes and optimization opportunities

### Geospatial Features
- **Service Provider Mapping**: Locate nearest recycling centers and waste management services
- **Multi-site Management**: Monitor multiple facilities from a single dashboard
- **Location-based Analytics**: Site-specific environmental performance

### Predictive Analytics
- **Consumption Forecasting**: Predict future energy usage patterns
- **Trend Analysis**: Identify seasonal patterns and anomalies
- **Optimization Recommendations**: AI-driven suggestions for efficiency improvements

## 🔧 Configuration

### MongoDB Setup
The system uses MongoDB for data storage. Ensure MongoDB is running on `localhost:27017` or update the connection string in `db_connect.py`:

```python
client = MongoClient("mongodb://your-mongodb-url:27017/")
```

### Environment Variables
Set the following environment variables for production:
- `MONGODB_URI`: MongoDB connection string
- `EMISSION_FACTOR`: Carbon emission factor (default: 0.82 kg CO₂/kWh)

## 📈 Analytics & Queries

The system includes pre-built aggregation pipelines for:

1. **Total Electricity Consumption**: Sum of all energy usage across sites
2. **Per-Asset Usage**: Individual equipment consumption analysis
3. **Daily/Monthly Patterns**: Time-based consumption trends
4. **Peak Usage Detection**: Identification of consumption spikes
5. **Carbon Footprint Calculation**: Automated CO₂ emissions tracking
6. **Geospatial Queries**: Nearest service provider location

## 🗂️ Data Models

### Telemetry Data
```json
{
  "timestamp": "2024-01-01T00:00:00",
  "asset_id": 101,
  "site_id": 1,
  "value_type": "electricity_kWh",
  "value": 18.36
}
```

### Sites
```json
{
  "site_id": 1,
  "name": "Raipur Plant",
  "location": {
    "type": "Point",
    "coordinates": [81.6296, 21.2514]
  }
}
```

### Assets
```json
{
  "asset_id": 101,
  "site_id": 1,
  "type": "electricity_meter",
  "name": "Main Meter A"
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the [Wiki](../../wiki) for detailed guides
- **Issues**: Report bugs via [GitHub Issues](../../issues)
- **Discussions**: Join the [community discussions](../../discussions)

## 🔮 Roadmap

- [ ] IoT device integration (MQTT/CoAP)
- [ ] Advanced ML models for predictive maintenance
- [ ] Multi-tenant architecture
- [ ] REST API development
- [ ] Mobile application
- [ ] Integration with popular ERP systems

---

**Akshita, IIIT-NR** 
