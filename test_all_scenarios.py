"""
SIH26161 - Test all scenarios
"""

from evacuation_engine import EvacuationDecisionEngine
from scenarios import SCENARIOS

for s_id, scenario in SCENARIOS.items():
    print("\n==========================================")
    print(f"Testing Scenario: {scenario['title']} ({s_id})")
    print("==========================================")
    
    decisions = EvacuationDecisionEngine.calculate_settlement_evacuation_deadlines(
        settlements=scenario["settlements"],
        road_network=scenario["road_network"],
        shelters=scenario["shelters"]
    )
    for d in decisions:
        print(f"  * {d['settlement_name']}: {d['decision_status']} -> {d['lsdt_display']}")
        if d["decision_status"] == "NO_VIABLE_ROUTE":
            print(f"    [!] NO VIABLE ROAD ROUTE ALERT: {d['action_directive']}")

print("\nAll scenario evaluations checked successfully!")
