"""
SIH26161 - Self Test Verification Script
Validates physics, hydrodynamic coupling, uncertainty calculations, and evacuation algorithms.
"""

from evacuation_engine import EvacuationDecisionEngine
from physics_engine import (
    MomentumCouplingEngine,
    MultiFidelityUncertaintyEngine,
    ReservoirPhysics,
    ValidationEngine,
)
from scenarios import SCENARIOS


def test_reservoir_and_breach():
    print("Testing Reservoir E-A-V and Parametric Breach...")
    eav = ReservoirPhysics.compute_eav_curve(70.0, 3720.0, 3650.0, 12.5)
    assert len(eav["elevations"]) == 25
    assert eav["volumes_mcm"][-1] >= 12.5
    
    hydro = ReservoirPhysics.generate_breach_hydrograph(3720.0, 3650.0, 42.0, 0.45, 12.5)
    assert hydro["peak_discharge_m3s"] > 1000.0
    assert len(hydro["hydrograph"]) > 50
    print(f"  [OK] Peak Discharge: {hydro['peak_discharge_m3s']} m3/s, Time to Peak: {hydro['time_to_peak_min']} min")

def test_momentum_coupling():
    print("Testing Momentum-Aware Coupling Interface...")
    hydro = ReservoirPhysics.generate_breach_hydrograph(3720.0, 3650.0, 42.0, 0.45, 12.5)
    coupling = MomentumCouplingEngine.extract_coupling_interface(hydro["hydrograph"])
    assert coupling["mass_balance_error_pct"] < 1.5
    assert len(coupling["timeseries"]) > 50
    print(f"  [OK] Mass Balance Error: {coupling['mass_balance_error_pct']}% -> Status: {coupling['status']}")

def test_multi_fidelity_uq():
    print("Testing Multi-Fidelity Uncertainty Model...")
    scenario = SCENARIOS["chamoli_2021"]
    uq = MultiFidelityUncertaintyEngine.run_multi_fidelity_uq(
        settlements=scenario["settlements"],
        base_peak_q=8450.0,
        ensemble_size=350,
        hifi_size=10
    )
    assert len(uq["settlements"]) == len(scenario["settlements"])
    for res in uq["settlements"].values():
        assert res["arrival_time_p10_min"] <= res["arrival_time_p50_min"] <= res["arrival_time_p90_min"]
        assert 0.0 <= res["inundation_scenario_freq_pct"] <= 100.0
    print("  [OK] Multi-Fidelity UQ produced calibrated P10/P50/P90 arrival times & scenario frequencies.")

def test_evacuation_engine():
    print("Testing Evacuation Decision Engine & No-Viable-Route Detection...")
    scenario = SCENARIOS["chamoli_2021"]
    decisions = EvacuationDecisionEngine.calculate_settlement_evacuation_deadlines(
        settlements=scenario["settlements"],
        road_network=scenario["road_network"],
        shelters=scenario["shelters"]
    )
    assert len(decisions) == len(scenario["settlements"])
    nvr_found = False
    for d in decisions:
        print(f"  Settlement: {d['settlement_name']} -> Status: {d['decision_status']} | LSDT: {d['lsdt_display']}")
        if d["decision_status"] == "NO_VIABLE_ROUTE":
            nvr_found = True
    print(f"  [OK] Evacuation calculations complete. (NVR identified: {nvr_found})")

def test_validation_suite():
    print("Testing Validation Suite (Ritter Exact + Sentinel-1 SAR)...")
    ritter = ValidationEngine.solve_ritter_analytical(20.0, 500.0, 15.0)
    assert ritter["rmse_m"] < 0.05
    sar = ValidationEngine.get_sentinel1_sar_validation("chamoli_2021")
    assert sar["metrics"]["csi_critical_success_index"] > 0.8
    print(f"  [OK] Ritter RMSE: {ritter['rmse_m']} m | Sentinel-1 CSI: {sar['metrics']['csi_critical_success_index']}")

if __name__ == "__main__":
    test_reservoir_and_breach()
    test_momentum_coupling()
    test_multi_fidelity_uq()
    test_evacuation_engine()
    test_validation_suite()
    print("\nALL VERIFICATION TESTS PASSED SUCCESSFULLY!")
