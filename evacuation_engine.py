"""
SIH26161 - Dam Break & Landslide-Lake Inundation Decision Support System
Evacuation Engine: Time-Dependent Road Network, Latest Safe Departure Time (LSDT),
No-Viable-Route (NVR) Detection, and Route Robustness Analysis.
"""

import math
from typing import Any


class EvacuationDecisionEngine:
    """
    Time-dependent evacuation graph routing.
    Evaluates dynamic edge traversability based on flood arrival time and depth thresholds.
    Calculates Latest Safe Departure Time (LSDT) and detects cut-off settlements (NO VIABLE ROUTE).
    """
    
    @staticmethod
    def evaluate_road_status_at_time(
        road_segments: list[dict[str, Any]],
        current_sim_time_min: float,
        critical_depth_m: float = 0.3,
        critical_hv_m2s: float = 0.5
    ) -> list[dict[str, Any]]:
        """
        Determines instantaneous safety state of each road segment at sim time t.
        States:
          - 'SAFE' (dry / depth < 0.1m)
          - 'CAUTION' (0.1m <= depth < critical_depth)
          - 'IMPASSABLE' (depth >= critical_depth OR h*v >= critical_hv)
        """
        updated_roads = []
        for rd in road_segments:
            arr_time = rd["flood_arrival_min"]
            peak_depth = rd["peak_depth_m"]
            velocity = rd["peak_velocity_ms"]
            
            # Dynamic depth at time t
            if current_sim_time_min < arr_time:
                cur_depth = 0.0
                cur_v = 0.0
            else:
                # Rising limb over 20 mins, then slow recession
                time_since_arr = current_sim_time_min - arr_time
                if time_since_arr < 25.0:
                    fraction = time_since_arr / 25.0
                    cur_depth = peak_depth * fraction
                    cur_v = velocity * fraction
                else:
                    cur_depth = max(0.1, peak_depth * math.exp(-0.015 * (time_since_arr - 25.0)))
                    cur_v = max(0.2, velocity * math.exp(-0.02 * (time_since_arr - 25.0)))
            
            hv = cur_depth * cur_v
            
            if cur_depth >= critical_depth_m or hv >= critical_hv_m2s:
                status = "IMPASSABLE"
                status_color = "#EF4444" # Crimson
            elif cur_depth >= 0.1:
                status = "CAUTION"
                status_color = "#F59E0B" # Amber
            else:
                status = "SAFE"
                status_color = "#22C55E" # Electric Green
                
            rd_copy = dict(rd)
            rd_copy["current_depth_m"] = round(cur_depth, 2)
            rd_copy["current_velocity_ms"] = round(cur_v, 2)
            rd_copy["current_hv_m2s"] = round(hv, 2)
            rd_copy["status"] = status
            rd_copy["status_color"] = status_color
            updated_roads.append(rd_copy)
            
        return updated_roads

    @staticmethod
    def calculate_settlement_evacuation_deadlines(
        settlements: list[dict[str, Any]],
        road_network: list[dict[str, Any]],
        shelters: list[dict[str, Any]],
        evacuation_speed_kmh: float = 25.0, # Mountain road convoy speed
        clearance_buffer_min: float = 15.0  # Safety buffer before road becomes unsafe
    ) -> list[dict[str, Any]]:
        """
        Calculates the Latest Safe Departure Time (LSDT) for each settlement.
        If a settlement's only escape routes are cut off before evacuation travel can finish,
        explicitly flags as 'NO VIABLE ROAD ROUTE' with emergency operational directive.
        """
        results = []
        road_lookup = {r["id"]: r for r in road_network}
        shelter_lookup = {s["id"]: s for s in shelters}
        
        for st in settlements:
            candidate_routes = st.get("routes_to_shelters", [])
            best_route_plan = None
            max_feasible_departure = -999.0
            
            for rt in candidate_routes:
                shelter_id = rt["shelter_id"]
                shelter = shelter_lookup.get(shelter_id, {"name": "Safe Zone", "capacity": 1000})
                segment_ids = rt["segment_ids"]
                total_distance_km = rt["distance_km"]
                travel_time_min = (total_distance_km / evacuation_speed_kmh) * 60.0
                
                # Find the earliest cutoff time along any segment of this route
                earliest_segment_cutoff = 9999.0
                bottleneck_segment = None
                
                for sid in segment_ids:
                    seg = road_lookup.get(sid)
                    if seg:
                        # Road becomes impassable when flood arrives
                        cutoff_t = seg["flood_arrival_min"]
                        if cutoff_t < earliest_segment_cutoff:
                            earliest_segment_cutoff = cutoff_t
                            bottleneck_segment = seg["name"]
                
                # Latest safe departure for this route:
                # Must reach the bottleneck before it cuts off!
                # Dep_time + travel_time_to_bottleneck <= earliest_segment_cutoff - buffer
                # conservative approximation: Dep_time <= earliest_segment_cutoff - travel_time_min - buffer
                lsdt_for_route = earliest_segment_cutoff - travel_time_min - clearance_buffer_min
                
                # Route is viable if LSDT > 0 (meaning you can still leave after t=0 breach initiation)
                is_viable = lsdt_for_route > 0.0
                
                if lsdt_for_route > max_feasible_departure:
                    max_feasible_departure = lsdt_for_route
                    best_route_plan = {
                        "shelter_id": shelter_id,
                        "shelter_name": shelter["name"],
                        "shelter_elevation_m": shelter["elevation_m"],
                        "distance_km": total_distance_km,
                        "travel_time_min": round(travel_time_min, 1),
                        "earliest_cutoff_min": round(earliest_segment_cutoff, 1),
                        "bottleneck_road": bottleneck_segment,
                        "lsdt_min": round(lsdt_for_route, 1),
                        "is_viable": is_viable,
                        "segments": segment_ids,
                        "robustness_pct": rt.get("robustness_pct", 88.0)
                    }
            
            # Evaluate settlement overall decision
            flood_arrival = st["nominal_arrival_time_min"]
            
            if best_route_plan is None or not best_route_plan["is_viable"]:
                # NO VIABLE ROAD ROUTE!
                decision_status = "NO_VIABLE_ROUTE"
                urgency = "CRITICAL"
                lsdt_display = "IMMEDIATE / AIR RESCUE ONLY"
                action_text = "Road corridors inundated before escape completion. Trigger High-Ground Vertical Shelter / NDRF Helilift protocol."
                time_to_flood_min = round(flood_arrival, 1)
            else:
                lsdt_val = best_route_plan["lsdt_min"]
                time_to_flood_min = round(flood_arrival, 1)
                
                if lsdt_val < 30.0:
                    decision_status = "URGENT_EVACUATION"
                    urgency = "HIGH"
                    action_text = f"Immediate evacuation convoy required. Must depart by T+{int(lsdt_val)} min towards {best_route_plan['shelter_name']}."
                elif lsdt_val < 90.0:
                    decision_status = "ACTIVE_EVACUATION"
                    urgency = "MEDIUM"
                    action_text = f"Initiate staged evacuation. Final departure deadline is T+{int(lsdt_val)} min."
                else:
                    decision_status = "MONITORING"
                    urgency = "LOW"
                    action_text = f"Sufficient lead time available. Prepare assets and stage transport before T+{int(lsdt_val)} min."
                    
                lsdt_display = f"T+{int(lsdt_val)} min ({int(lsdt_val // 60):02d}h {int(lsdt_val % 60):02d}m)"
                
            results.append({
                "settlement_id": st["id"],
                "settlement_name": st["name"],
                "population": st["population"],
                "elevation_m": st["elevation_m"],
                "dist_from_dam_km": st["dist_from_dam_km"],
                "flood_arrival_min": time_to_flood_min,
                "decision_status": decision_status,
                "urgency": urgency,
                "lsdt_display": lsdt_display,
                "lsdt_numeric_min": round(max_feasible_departure, 1) if max_feasible_departure > -900 else -1.0,
                "action_directive": action_text,
                "best_route": best_route_plan,
                "hazard_depth_m": st["nominal_depth_m"],
                "hazard_velocity_ms": st["nominal_velocity_ms"],
                "exposure_summary": {
                    "buildings_exposed": st.get("buildings_count", int(st["population"] / 4.2)),
                    "schools": st.get("schools", 1),
                    "hospitals": st.get("hospitals", 0),
                    "cropland_ha": st.get("cropland_ha", 45)
                }
            })
            
        return results
