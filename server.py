"""
SIH26161 - Dam Break & Landslide-Lake Inundation Decision Support System
FastAPI Application Server & Scientific Computing Gateway
"""

import math
import os

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from evacuation_engine import EvacuationDecisionEngine
from physics_engine import (
    MomentumCouplingEngine,
    MultiFidelityUncertaintyEngine,
    ReservoirPhysics,
    ValidationEngine,
)
from scenarios import SCENARIOS

app = FastAPI(
    title="SIH26161 Dam Break & Inundation Decision Support System",
    description="Physics-based, uncertainty-aware HADR intelligence platform for NDRF/DDMA/NTRO",
    version="1.0.0"
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EvacRecalcRequest(BaseModel):
    scenario_id: str
    evacuation_speed_kmh: float = 25.0
    clearance_buffer_min: float = 15.0
    critical_depth_m: float = 0.3
    critical_hv_m2s: float = 0.5


@app.get("/api/scenarios")
def list_scenarios():
    """List all available disaster case scenarios."""
    summary = []
    for s in SCENARIOS.values():
        summary.append({
            "id": s["id"],
            "title": s["title"],
            "subtitle": s["subtitle"],
            "region": s["region"],
            "dam_type": s["dam_type"],
            "event_date": s["event_date"],
            "location": s["location"]
        })
    return {"scenarios": summary}


@app.get("/api/scenario/{scenario_id}")
def get_scenario_details(scenario_id: str):
    """Returns the full computed physics and decision intelligence bundle for a scenario."""
    if scenario_id not in SCENARIOS:
        raise HTTPException(status_code=404, detail="Scenario not found")
        
    s = SCENARIOS[scenario_id]
    res_meta = s["reservoir"]
    
    # 1. Compute E-A-V Curve
    eav_data = ReservoirPhysics.compute_eav_curve(
        dam_height=res_meta["dam_height_m"],
        crest_elevation=res_meta["crest_elevation_m"],
        base_elevation=res_meta["dam_base_elev_m"],
        max_storage_mcm=res_meta["max_storage_mcm"]
    )
    
    # 2. Compute Parametric Breach Hydrograph
    hydro_data = ReservoirPhysics.generate_breach_hydrograph(
        initial_water_level=res_meta["initial_water_level_m"],
        dam_base_elev=res_meta["dam_base_elev_m"],
        breach_width=res_meta["breach_width_m"],
        breach_formation_time_hrs=res_meta["breach_formation_time_hrs"],
        reservoir_vol_mcm=res_meta["max_storage_mcm"]
    )
    
    # 3. Extract SPH -> Delft3D Momentum-Aware Coupling Interface
    coupling_data = MomentumCouplingEngine.extract_coupling_interface(
        hydrograph_data=hydro_data["hydrograph"],
        channel_slope=s["river_channel"]["avg_slope"],
        manning_n=s["river_channel"]["manning_n"]
    )
    
    # 4. Multi-Fidelity Uncertainty Quantification & Discrepancy Correction
    uq_data = MultiFidelityUncertaintyEngine.run_multi_fidelity_uq(
        settlements=s["settlements"],
        base_peak_q=hydro_data["peak_discharge_m3s"]
    )
    
    # 5. Calculate Time-Dependent Evacuation Deadlines (LSDT & NVR)
    evac_decisions = EvacuationDecisionEngine.calculate_settlement_evacuation_deadlines(
        settlements=s["settlements"],
        road_network=s["road_network"],
        shelters=s["shelters"],
        evacuation_speed_kmh=25.0,
        clearance_buffer_min=15.0
    )
    
    # 6. Initial Road Safety Evaluation (t=0)
    initial_roads = EvacuationDecisionEngine.evaluate_road_status_at_time(
        road_segments=s["road_network"],
        current_sim_time_min=0.0
    )
    
    return {
        "metadata": {
            "id": s["id"],
            "title": s["title"],
            "subtitle": s["subtitle"],
            "region": s["region"],
            "event_date": s["event_date"],
            "dam_type": s["dam_type"],
            "location": s["location"]
        },
        "reservoir": res_meta,
        "river_channel": s["river_channel"],
        "eav_curve": eav_data,
        "breach_hydrograph": hydro_data,
        "momentum_coupling": coupling_data,
        "multi_fidelity_uq": uq_data,
        "settlements": s["settlements"],
        "shelters": s["shelters"],
        "road_network": initial_roads,
        "evacuation_decisions": evac_decisions
    }


@app.post("/api/evacuation/recalculate")
def recalculate_evacuation(req: EvacRecalcRequest):
    """Interactive re-routing with custom convoy speed, buffer, and flood depth limits."""
    if req.scenario_id not in SCENARIOS:
        raise HTTPException(status_code=404, detail="Scenario not found")
        
    s = SCENARIOS[req.scenario_id]
    
    decisions = EvacuationDecisionEngine.calculate_settlement_evacuation_deadlines(
        settlements=s["settlements"],
        road_network=s["road_network"],
        shelters=s["shelters"],
        evacuation_speed_kmh=req.evacuation_speed_kmh,
        clearance_buffer_min=req.clearance_buffer_min
    )
    
    return {
        "scenario_id": req.scenario_id,
        "parameters": {
            "evacuation_speed_kmh": req.evacuation_speed_kmh,
            "clearance_buffer_min": req.clearance_buffer_min,
            "critical_depth_m": req.critical_depth_m
        },
        "evacuation_decisions": decisions
    }


@app.get("/api/simulation/frame/{scenario_id}")
def get_simulation_frame(
    scenario_id: str,
    time_min: float = Query(0.0, ge=0.0, le=360.0),
    critical_depth_m: float = Query(0.3, ge=0.1, le=2.0)
):
    """Returns dynamic time-step status for the map at time t (mins)."""
    if scenario_id not in SCENARIOS:
        raise HTTPException(status_code=404, detail="Scenario not found")
        
    s = SCENARIOS[scenario_id]
    
    # 1. Update dynamic road statuses
    updated_roads = EvacuationDecisionEngine.evaluate_road_status_at_time(
        road_segments=s["road_network"],
        current_sim_time_min=time_min,
        critical_depth_m=critical_depth_m
    )
    
    # 2. Compute wave front position along the river
    # Average wave front celerity ~ 5.5 - 7.5 m/s in mountain canyon
    wave_front_distance_km = min(s["river_channel"]["length_km"], (time_min * 60.0 * 6.2) / 1000.0)
    
    # 3. Settlement status at time t
    settlement_statuses = []
    for st in s["settlements"]:
        arr_t = st["nominal_arrival_time_min"]
        is_flooded = time_min >= arr_t
        time_to_impact = max(0.0, arr_t - time_min)
        
        if is_flooded:
            elapsed = time_min - arr_t
            if elapsed < 20.0:
                current_depth = st["nominal_depth_m"] * (elapsed / 20.0)
                current_v = st["nominal_velocity_ms"] * (elapsed / 20.0)
            else:
                current_depth = max(0.2, st["nominal_depth_m"] * math.exp(-0.012 * (elapsed - 20.0)))
                current_v = max(0.5, st["nominal_velocity_ms"] * math.exp(-0.015 * (elapsed - 20.0)))
            stage = "FLOODED"
        else:
            current_depth = 0.0
            current_v = 0.0
            stage = "IMMINENT_RISK" if time_to_impact <= 30.0 else "PREPARING"
            
        settlement_statuses.append({
            "id": st["id"],
            "name": st["name"],
            "stage": stage,
            "is_flooded": is_flooded,
            "time_to_impact_min": round(time_to_impact, 1),
            "current_depth_m": round(current_depth, 2),
            "current_velocity_ms": round(current_v, 2),
            "hazard_rating_hv": round(current_depth * current_v, 2)
        })
        
    return {
        "scenario_id": scenario_id,
        "time_min": time_min,
        "wave_front_distance_km": round(wave_front_distance_km, 2),
        "total_river_length_km": s["river_channel"]["length_km"],
        "road_network": updated_roads,
        "settlements": settlement_statuses
    }


@app.get("/api/validation/{scenario_id}")
def get_validation_data(scenario_id: str):
    """Returns Ritter analytical solution and Sentinel-1 SAR earth observation validation data."""
    if scenario_id not in SCENARIOS:
        raise HTTPException(status_code=404, detail="Scenario not found")
        
    ritter_data = ValidationEngine.solve_ritter_analytical(h0=20.0, t_sec=15.0)
    sar_data = ValidationEngine.get_sentinel1_sar_validation(scenario_id=scenario_id)
    
    return {
        "scenario_id": scenario_id,
        "analytical_ritter": ritter_data,
        "sentinel1_sar": sar_data,
        "summary": "Three-level validation architecture: Analytical Solver (Ritter), Flume Benchmark, and Satellite Real-Event Extent (Sentinel-1 SAR)."
    }


@app.get("/api/eap-report/{scenario_id}")
def generate_eap_report(scenario_id: str):
    """Generates official NDRF / DDMA Emergency Action Plan (EAP) Bulletin."""
    if scenario_id not in SCENARIOS:
        raise HTTPException(status_code=404, detail="Scenario not found")
        
    s = SCENARIOS[scenario_id]
    evac_decisions = EvacuationDecisionEngine.calculate_settlement_evacuation_deadlines(
        settlements=s["settlements"],
        road_network=s["road_network"],
        shelters=s["shelters"]
    )
    
    total_exposed_pop = sum(st["population"] for st in s["settlements"])
    nvr_settlements = [d for d in evac_decisions if d["decision_status"] == "NO_VIABLE_ROUTE"]
    urgent_settlements = [d for d in evac_decisions if d["decision_status"] == "URGENT_EVACUATION"]
    
    return {
        "bulletin_id": f"EAP-NDRF-{scenario_id.upper()}-001",
        "issued_by": "National Disaster Response Force (NDRF) / NTRO Hydro-Inundation Cell",
        "scenario_title": s["title"],
        "region": s["region"],
        "total_exposed_population": total_exposed_pop,
        "critical_nvr_count": len(nvr_settlements),
        "urgent_evac_count": len(urgent_settlements),
        "settlements_decision_matrix": evac_decisions,
        "command_directives": [
            "1. Activate SDRF / Indian Army Aviation units for high-ground vertical rescue in identified NO-VIABLE-ROUTE zones.",
            "2. Establish traffic check-posts at primary arterial bottlenecks before flood arrival thresholds.",
            "3. Broadcast automated wireless emergency alerts (WEA) with specific settlement Latest Safe Departure Times.",
            "4. Enforce strict closure of low-lying bridges and culverts exceeding 0.3m inundation or 0.5 m2/s hazard rating."
        ]
    }

# Mount static directory for frontend
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
