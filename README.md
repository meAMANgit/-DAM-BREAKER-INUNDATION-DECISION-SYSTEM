# 🌊 DAM BREAKER & INUNDATION DECISION SUPPORT SYSTEM (SIH26161)

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Three.js](https://img.shields.io/badge/Three.js-WebGL-000000?style=for-the-badge&logo=threedotjs&logoColor=white)](https://threejs.org)
[![Leaflet](https://img.shields.io/badge/Leaflet-GIS_Maps-199900?style=for-the-badge&logo=leaflet&logoColor=white)](https://leafletjs.com)
[![Tests](https://img.shields.io/badge/Tests-100%25_Passing-brightgreen?style=for-the-badge&logo=pytest&logoColor=white)](https://pytest.org)

> **SIH26161**: High-Fidelity Dam Break & Landslide-Lake Inundation Modeling Tactical Decision Support System  
> *Developed for National Disaster Management Authorities (NDRF / DDMA / NTRO / SDMA / CWC).*

---

## 🎯 Operational Mission

Traditional hydraulic inundation tools answer only *"Where does the flood water go?"*  
**DAM BREAKER** transforms physical hydrodynamic simulations into **actionable emergency response intelligence**:

1. **⏱️ When will the flood wave hit each settlement?** (High-precision arrival time envelopes)
2. **🛣️ When will roads become impassable?** (Dynamic depth $h(t) \ge 0.3\,\text{m}$ cut-off detection)
3. **⏳ What is the Latest Safe Departure Time (LSDT)?** (Time-dependent reverse Dijkstra from high-elevation safe zones)
4. **🚁 Which settlements are Cut-Off (No Viable Road Route - NVR)?** (Early triggers for vertical evacuation / aerial airlift)

---

## 🏗️ System Architecture & Physics

```
                                  ┌───────────────────────────────┐
                                  │   Reservoir / Landslide Lake  │
                                  │    E-A-V Rating Curves & Q(t) │
                                  └───────────────┬───────────────┘
                                                  │
                                                  ▼
                                  ┌───────────────────────────────┐
                                  │  Near-Field SPH Fluid Solver  │
                                  │   Violent 3D Jet / Free Surf  │
                                  └───────────────┬───────────────┘
                                                  │
                             [ Momentum-Aware Control Plane Interface ]
                             [ Q(t), |u_mag|(t), u_dir(t), Mass Err < 1.5% ]
                                                  │
                                                  ▼
                                  ┌───────────────────────────────┐
                                  │  Far-Field 2D Shallow Water   │
                                  │    Delft3D Hydrodynamics      │
                                  └───────────────┬───────────────┘
                                                  │
                                                  ▼
                                  ┌───────────────────────────────┐
                                  │   Multi-Fidelity UQ Engine    │
                                  │ 350 Cheap + 10 HiFi + GP Corr │
                                  └───────────────┬───────────────┘
                                                  │
                                                  ▼
                                  ┌───────────────────────────────┐
                                  │ Time-Dependent Evacuation Net │
                                  │ LSDT & No-Viable-Route Alert  │
                                  └───────────────┬───────────────┘
                                                  │
                                                  ▼
                                  ┌───────────────────────────────┐
                                  │ Tactical HADR Command Center  │
                                  │   GIS Map + 3D SPH + EAP PDF  │
                                  └───────────────────────────────┘
```

---

## ✨ Key Features

- **🌊 3D SPH Lagrangian Fluid Simulation (Three.js WebGL)**:
  - 16,000+ SPH particles simulating plunging vertical jets, air entrainment, turbulent aeration foam, and gorge bed friction.
  - Momentum-aware coupling control plane at $0.85\,\text{km}$ downstream with $<1.5\%$ mass balance error.

- **🗺️ GIS Tactical Inundation Map (Leaflet & Canvas)**:
  - Live 2D hydrodynamic flow particles that dynamically scale and track wave front arrival.
  - Color-coded road hazards: Safe ($h < 0.1\,\text{m}$), Caution ($0.1 \le h < 0.3\,\text{m}$), Cut-Off ($h \ge 0.3\,\text{m}$).
  - Safe shelter hubs and settlement popups.

- **📈 Multi-Fidelity Uncertainty Quantification (UQ)**:
  - Combines 350 rapid 1D parametric runs with 10 high-fidelity coupled 3D/2D simulations calibrated via a Gaussian Process discrepancy model.
  - Provides $P10 - P50 - P90$ arrival confidence intervals.

- **📜 Three-Tier Scientific Validation**:
  - **Tier 1 (Analytical)**: Ritter 1D analytical dam-break exact solution comparison ($RMSE = 0.0163\,\text{m}$).
  - **Tier 2 (Laboratory)**: USACE / IAHR flume benchmark compliance ($Froude > 1.8$).
  - **Tier 3 (Satellite Earth Observation)**: Sentinel-1 SAR spatial overpass validation with $CSI = 0.833$ and $F1 = 0.909$.

- **📋 NDRF / DDMA Emergency Action Plan (EAP) Generator**:
  - Auto-generated operational matrix with LSDT deadlines, designated shelter assignments, and printable official directives.

---

## 📂 Included Disaster Scenarios

1. **Chamoli / Rishi Ganga (Feb 2021 GLOF Real Case)**:
   - Rock-ice avalanche trigger ($27\,\text{MCM}$), Ronti/Rishi Ganga steep canyon, Raini & Tapovan downstream infrastructure.
2. **Tehri Dam High-Head Overtopping Simulation**:
   - $260.5\,\text{m}$ rock-fill high dam overtopping wave propagation down the Bhagirathi river towards Devprayag & Rishikesh.
3. **Phuktal River Landslide Lake (Zanskar 2015)**:
   - River blockage dam breach with dynamic high-altitude valley road cut-offs in Ladakh.

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+
- Modern Web Browser (Chrome / Edge / Firefox)

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/meAMANgit/-DAM-BREAKER-INUNDATION-DECISION-SYSTEM.git
cd -DAM-BREAKER-INUNDATION-DECISION-SYSTEM

# Install dependencies
pip install fastapi uvicorn pytest numpy scipy ruff
```

### 3. Running the Server
```bash
# Start FastAPI application
python server.py
# Or using uvicorn directly:
python -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload
```

### 4. Open in Browser
Open your browser and navigate to:
👉 **`http://127.0.0.1:8000`**

---

## 🧪 Running Test Suites

```bash
# Run all unit and scenario test suites
python -m pytest test_system.py test_all_scenarios.py -v

# Run code linter
python -m ruff check .
```

---

## 📡 API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/scenarios` | List all available disaster scenarios |
| `GET` | `/api/scenario/{scenario_id}` | Retrieve complete hydrodynamic dataset & road network for scenario |
| `GET` | `/api/simulation/frame/{scenario_id}` | Get dynamic wave front position & road depths at time $t$ |
| `POST` | `/api/evacuation/recalculate` | Dynamic evacuation LSDT re-calculation on speed/buffer tuning |
| `GET` | `/api/validation/{scenario_id}` | Retrieve Ritter analytical, Flume, & Sentinel-1 SAR validation datasets |
| `GET` | `/api/eap-report/{scenario_id}` | Generate official NDRF / DDMA Emergency Action Plan bulletin |

---

## ⚖️ Scientific Integrity Notice
> Inundation probabilities in this decision support system represent **Scenario Frequency** (% of plausible sampled breach hydrographs inundating a specific node), not structural dam failure probability.

---

## 👥 Contributors & Acknowledgements
- **Team**: IIIT Kottayam
- **Problem Statement**: SIH26161 (Disaster Management / HADR Decision Support)
- **Stakeholders**: NTRO, NDRF, CWC, NDMA
