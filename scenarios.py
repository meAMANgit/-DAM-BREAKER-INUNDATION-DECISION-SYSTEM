"""
SIH26161 - Scenarios Database
Comprehensive disaster cases:
1. Chamoli / Rishi Ganga 2021 (Real-world HADR Case with Sentinel-1 SAR Overpass)
2. Tehri Himalayan High-Head Dam Breach (Major Infrastructure Simulation)
3. Phuktal / Zanskar Landslide-Dammed Lake 2015 (Remote Valley Natural Dam Failure)
"""

from typing import Any

SCENARIOS: dict[str, Any] = {
    "chamoli_2021": {
        "id": "chamoli_2021",
        "title": "Chamoli / Rishi Ganga Disaster (Feb 2021)",
        "subtitle": "Landslide-Dammed Lake & Glacial Rock-Ice Surge Breach",
        "region": "Garhwal Himalaya, Uttarakhand, India",
        "event_date": "07 Feb 2021, 04:45 UTC (10:15 IST)",
        "dam_type": "Landslide & Debris Blockage Lake",
        "location": {"lat": 30.485, "lng": 79.725, "zoom": 12},
        "reservoir": {
            "initial_water_level_m": 3720.0,
            "dam_base_elev_m": 3650.0,
            "dam_height_m": 70.0,
            "crest_elevation_m": 3720.0,
            "max_storage_mcm": 12.5,
            "breach_width_m": 42.0,
            "breach_formation_time_hrs": 0.45,
            "nominal_peak_q_m3s": 8450.0,
            "sediment_concentration_pct": 35.0
        },
        "river_channel": {
            "name": "Rishi Ganga -> Dhauli Ganga Gorge",
            "length_km": 32.0,
            "avg_slope": 0.038,
            "manning_n": 0.052,
            "path_coordinates": [
                [30.4850, 79.7250, 3650], # Dam / Lake Breakout
                [30.4910, 79.7120, 3420], # Upper Rishi Ganga Canyon
                [30.4950, 79.7010, 3180], # SPH-Delft3D Coupling Plane (0.85 km)
                [30.5020, 79.6890, 2900], # Rishi Ganga / Dhauli Ganga Confluence
                [30.4990, 79.6740, 2450], # Raini Village Valley Floor
                [30.5120, 79.6580, 2120], # Tapovan Hydro Power Tunnel & Barrage
                [30.5250, 79.6350, 1940], # Dhak Stream Bend
                [30.5480, 79.5980, 1620], # Joshimath Lower Valley Foot
                [30.5620, 79.5650, 1420]  # Helang Alaknanda Gateway
            ]
        },
        "settlements": [
            {
                "id": "st_raini",
                "name": "Raini Village (Upper & Lower)",
                "lat": 30.4985,
                "lng": 79.6760,
                "elevation_m": 2040,
                "elevation_diff_m": 1610,
                "dist_from_dam_km": 4.8,
                "population": 480,
                "nominal_arrival_time_min": 14.5,
                "nominal_depth_m": 12.8,
                "nominal_velocity_ms": 14.2,
                "buildings_count": 82,
                "schools": 1,
                "hospitals": 0,
                "routes_to_shelters": [
                    {
                        "shelter_id": "sh_joshimath",
                        "distance_km": 14.2,
                        "segment_ids": ["rd_raini_bridge", "rd_raini_tapovan", "rd_tapovan_joshimath"],
                        "robustness_pct": 8.0 # Very low because Raini Bridge gets severed within 14 mins!
                    },
                    {
                        "shelter_id": "sh_raini_high",
                        "distance_km": 1.2,
                        "segment_ids": ["rd_raini_ridge_trail"],
                        "robustness_pct": 94.0 # High ground foot trail
                    }
                ]
            },
            {
                "id": "st_tapovan",
                "name": "Tapovan Project & Township",
                "lat": 30.5115,
                "lng": 79.6565,
                "elevation_m": 1820,
                "elevation_diff_m": 1830,
                "dist_from_dam_km": 8.2,
                "population": 920,
                "nominal_arrival_time_min": 26.0,
                "nominal_depth_m": 15.4,
                "nominal_velocity_ms": 12.8,
                "buildings_count": 165,
                "schools": 1,
                "hospitals": 1,
                "routes_to_shelters": [
                    {
                        "shelter_id": "sh_joshimath",
                        "distance_km": 10.5,
                        "segment_ids": ["rd_tapovan_dhak", "rd_dhak_joshimath"],
                        "robustness_pct": 32.0 # Road gets cut at Dhak Bridge at T+38m
                    },
                    {
                        "shelter_id": "sh_tapovan_helipad",
                        "distance_km": 2.1,
                        "segment_ids": ["rd_tapovan_ridge"],
                        "robustness_pct": 88.0
                    }
                ]
            },
            {
                "id": "st_dhak",
                "name": "Dhak Settlement",
                "lat": 30.5260,
                "lng": 79.6320,
                "elevation_m": 1680,
                "elevation_diff_m": 1970,
                "dist_from_dam_km": 13.5,
                "population": 650,
                "nominal_arrival_time_min": 42.0,
                "nominal_depth_m": 8.5,
                "nominal_velocity_ms": 9.4,
                "buildings_count": 110,
                "schools": 1,
                "hospitals": 0,
                "routes_to_shelters": [
                    {
                        "shelter_id": "sh_joshimath",
                        "distance_km": 7.4,
                        "segment_ids": ["rd_dhak_joshimath"],
                        "robustness_pct": 91.0 # High terrace road
                    }
                ]
            },
            {
                "id": "st_joshimath_lower",
                "name": "Joshimath Lower Gateway",
                "lat": 30.5470,
                "lng": 79.5960,
                "elevation_m": 1490,
                "elevation_diff_m": 2160,
                "dist_from_dam_km": 21.0,
                "population": 2100,
                "nominal_arrival_time_min": 68.0,
                "nominal_depth_m": 6.2,
                "nominal_velocity_ms": 7.1,
                "buildings_count": 340,
                "schools": 3,
                "hospitals": 1,
                "routes_to_shelters": [
                    {
                        "shelter_id": "sh_joshimath_upper",
                        "distance_km": 3.8,
                        "segment_ids": ["rd_joshimath_arterial"],
                        "robustness_pct": 99.0
                    }
                ]
            },
            {
                "id": "st_helang",
                "name": "Helang Confluence Station",
                "lat": 30.5630,
                "lng": 79.5630,
                "elevation_m": 1310,
                "elevation_diff_m": 2340,
                "dist_from_dam_km": 29.5,
                "population": 780,
                "nominal_arrival_time_min": 92.0,
                "nominal_depth_m": 5.4,
                "nominal_velocity_ms": 6.3,
                "buildings_count": 140,
                "schools": 1,
                "hospitals": 0,
                "routes_to_shelters": [
                    {
                        "shelter_id": "sh_pipalkoti_safe",
                        "distance_km": 12.0,
                        "segment_ids": ["rd_helang_nh07"],
                        "robustness_pct": 95.0
                    }
                ]
            }
        ],
        "shelters": [
            {
                "id": "sh_raini_high",
                "name": "Raini High Ridge Terrace Safe Zone",
                "lat": 30.5030,
                "lng": 79.6730,
                "elevation_m": 2280,
                "capacity": 600,
                "type": "High-Ground Natural Plateau"
            },
            {
                "id": "sh_tapovan_helipad",
                "name": "Tapovan Upper Army Helipad & Camp",
                "lat": 30.5180,
                "lng": 79.6510,
                "elevation_m": 2010,
                "capacity": 1200,
                "type": "Designated Evacuation Helipad"
            },
            {
                "id": "sh_joshimath",
                "name": "Joshimath Cantt Relief Center",
                "lat": 30.5540,
                "lng": 79.5720,
                "elevation_m": 1920,
                "capacity": 3500,
                "type": "Primary Multi-Service Shelter"
            },
            {
                "id": "sh_joshimath_upper",
                "name": "Joshimath Sports Ground Safe Hub",
                "lat": 30.5590,
                "lng": 79.5690,
                "elevation_m": 2050,
                "capacity": 2500,
                "type": "Municipal Relief Camp"
            },
            {
                "id": "sh_pipalkoti_safe",
                "name": "Pipalkoti Inter-College Shelter",
                "lat": 30.5750,
                "lng": 79.5280,
                "elevation_m": 1580,
                "capacity": 2000,
                "type": "District Disaster Center"
            }
        ],
        "road_network": [
            {
                "id": "rd_raini_bridge",
                "name": "Raini Strategic RCC Bridge (NH-58 Ext)",
                "length_km": 0.4,
                "elevation_m": 1940,
                "flood_arrival_min": 14.5,
                "peak_depth_m": 14.2,
                "peak_velocity_ms": 15.5,
                "coordinates": [[30.4975, 79.6765], [30.4995, 79.6755]]
            },
            {
                "id": "rd_raini_ridge_trail",
                "name": "Raini Upper Cliff Evacuation Footway",
                "length_km": 1.2,
                "elevation_m": 2200,
                "flood_arrival_min": 999.0, # Elevated cliff safe
                "peak_depth_m": 0.0,
                "peak_velocity_ms": 0.0,
                "coordinates": [[30.4985, 79.6760], [30.5030, 79.6730]]
            },
            {
                "id": "rd_raini_tapovan",
                "name": "Dhauli Ganga Gorge Road (Raini - Tapovan)",
                "length_km": 4.5,
                "elevation_m": 1880,
                "flood_arrival_min": 20.0,
                "peak_depth_m": 12.0,
                "peak_velocity_ms": 13.0,
                "coordinates": [[30.4995, 79.6755], [30.5115, 79.6565]]
            },
            {
                "id": "rd_tapovan_dhak",
                "name": "Tapovan Lower Valley Link & Bridge",
                "length_km": 3.8,
                "elevation_m": 1740,
                "flood_arrival_min": 32.0,
                "peak_depth_m": 11.2,
                "peak_velocity_ms": 11.5,
                "coordinates": [[30.5115, 79.6565], [30.5260, 79.6320]]
            },
            {
                "id": "rd_tapovan_ridge",
                "name": "Tapovan Upper Slope Access Road",
                "length_km": 2.1,
                "elevation_m": 1980,
                "flood_arrival_min": 999.0,
                "peak_depth_m": 0.0,
                "peak_velocity_ms": 0.0,
                "coordinates": [[30.5115, 79.6565], [30.5180, 79.6510]]
            },
            {
                "id": "rd_dhak_joshimath",
                "name": "Dhak - Joshimath Valley Highway",
                "length_km": 6.8,
                "elevation_m": 1690,
                "flood_arrival_min": 52.0,
                "peak_depth_m": 5.8,
                "peak_velocity_ms": 6.5,
                "coordinates": [[30.5260, 79.6320], [30.5470, 79.5960]]
            },
            {
                "id": "rd_joshimath_arterial",
                "name": "Joshimath Cantt Incline Road",
                "length_km": 3.8,
                "elevation_m": 1820,
                "flood_arrival_min": 999.0,
                "peak_depth_m": 0.0,
                "peak_velocity_ms": 0.0,
                "coordinates": [[30.5470, 79.5960], [30.5590, 79.5690]]
            },
            {
                "id": "rd_helang_nh07",
                "name": "National Highway NH-07 Corridor",
                "length_km": 12.0,
                "elevation_m": 1420,
                "flood_arrival_min": 115.0,
                "peak_depth_m": 3.2,
                "peak_velocity_ms": 4.1,
                "coordinates": [[30.5630, 79.5630], [30.5750, 79.5280]]
            }
        ]
    },
    
    "tehri_himalayan": {
        "id": "tehri_himalayan",
        "title": "Tehri Dam High-Head Breach Scenario",
        "subtitle": "Earth & Rockfill Mega-Dam Overtopping / Piping Simulation",
        "region": "Bhagirathi River Valley, Uttarakhand, India",
        "event_date": "Simulated Monsoon Super-Spillway Jam",
        "dam_type": "Earth and Rock-Fill Dam (260.5m Head)",
        "location": {"lat": 30.378, "lng": 78.480, "zoom": 11},
        "reservoir": {
            "initial_water_level_m": 830.0,
            "dam_base_elev_m": 570.0,
            "dam_height_m": 260.5,
            "crest_elevation_m": 839.5,
            "max_storage_mcm": 3540.0,
            "breach_width_m": 120.0,
            "breach_formation_time_hrs": 1.8,
            "nominal_peak_q_m3s": 65400.0,
            "sediment_concentration_pct": 18.0
        },
        "river_channel": {
            "name": "Bhagirathi -> Ganga Mainstem",
            "length_km": 78.0,
            "avg_slope": 0.009,
            "manning_n": 0.038,
            "path_coordinates": [
                [30.3780, 78.4800, 570], # Tehri Dam Toe
                [30.3420, 78.5120, 520], # Koteshwar Re-regulating Dam
                [30.2850, 78.5450, 480], # SPH-Delft3D Control Interface (1.2 km)
                [30.1450, 78.5980, 440], # Devprayag Confluence
                [30.1120, 78.4720, 390], # Kaudiyala Canyon
                [30.0890, 78.3650, 350], # Shivpuri Rapids
                [30.0860, 78.2670, 310], # Rishikesh (Laxman Jhula / Barrage)
                [29.9450, 78.1640, 275]  # Haridwar Ghats & Floodplain
            ]
        },
        "settlements": [
            {
                "id": "st_koteshwar",
                "name": "Koteshwar Settlement",
                "lat": 30.3380,
                "lng": 78.5150,
                "elevation_m": 535,
                "elevation_diff_m": 35,
                "dist_from_dam_km": 8.5,
                "population": 1450,
                "nominal_arrival_time_min": 18.0,
                "nominal_depth_m": 28.5,
                "nominal_velocity_ms": 16.4,
                "buildings_count": 280,
                "schools": 2,
                "hospitals": 1,
                "routes_to_shelters": [
                    {
                        "shelter_id": "sh_koteshwar_hill",
                        "distance_km": 2.5,
                        "segment_ids": ["rd_koteshwar_ascent"],
                        "robustness_pct": 92.0
                    }
                ]
            },
            {
                "id": "st_devprayag",
                "name": "Devprayag Sangam Town",
                "lat": 30.1450,
                "lng": 78.5980,
                "elevation_m": 455,
                "elevation_diff_m": 115,
                "dist_from_dam_km": 36.0,
                "population": 5200,
                "nominal_arrival_time_min": 58.0,
                "nominal_depth_m": 21.0,
                "nominal_velocity_ms": 11.2,
                "buildings_count": 890,
                "schools": 4,
                "hospitals": 2,
                "routes_to_shelters": [
                    {
                        "shelter_id": "sh_devprayag_ridge",
                        "distance_km": 3.2,
                        "segment_ids": ["rd_devprayag_bridge", "rd_devprayag_cliff"],
                        "robustness_pct": 45.0
                    }
                ]
            },
            {
                "id": "st_rishikesh",
                "name": "Rishikesh Holy Plains Gateway",
                "lat": 30.0860,
                "lng": 78.2670,
                "elevation_m": 320,
                "elevation_diff_m": 250,
                "dist_from_dam_km": 64.0,
                "population": 102000,
                "nominal_arrival_time_min": 118.0,
                "nominal_depth_m": 14.5,
                "nominal_velocity_ms": 7.8,
                "buildings_count": 16400,
                "schools": 24,
                "hospitals": 8,
                "routes_to_shelters": [
                    {
                        "shelter_id": "sh_aiims_rishikesh",
                        "distance_km": 5.6,
                        "segment_ids": ["rd_rishikesh_bypass"],
                        "robustness_pct": 96.0
                    }
                ]
            },
            {
                "id": "st_haridwar",
                "name": "Haridwar Urban Plain",
                "lat": 29.9450,
                "lng": 78.1640,
                "elevation_m": 280,
                "elevation_diff_m": 290,
                "dist_from_dam_km": 82.0,
                "population": 310000,
                "nominal_arrival_time_min": 175.0,
                "nominal_depth_m": 8.2,
                "nominal_velocity_ms": 4.5,
                "buildings_count": 52000,
                "schools": 65,
                "hospitals": 18,
                "routes_to_shelters": [
                    {
                        "shelter_id": "sh_bhel_highland",
                        "distance_km": 8.2,
                        "segment_ids": ["rd_haridwar_nh58"],
                        "robustness_pct": 98.0
                    }
                ]
            }
        ],
        "shelters": [
            {
                "id": "sh_koteshwar_hill",
                "name": "Koteshwar CISF Hill Campus",
                "lat": 30.3450,
                "lng": 78.5220,
                "elevation_m": 720,
                "capacity": 2000,
                "type": "Armed Reserve High Ground"
            },
            {
                "id": "sh_devprayag_ridge",
                "name": "Devprayag Degree College Plateau",
                "lat": 30.1520,
                "lng": 78.6050,
                "elevation_m": 680,
                "capacity": 6000,
                "type": "Institutional Safe Hub"
            },
            {
                "id": "sh_aiims_rishikesh",
                "name": "AIIMS Rishikesh Elevated Relief Hospital",
                "lat": 30.0750,
                "lng": 78.2880,
                "elevation_m": 375,
                "capacity": 25000,
                "type": "Tertiary Medical & Trauma Base"
            },
            {
                "id": "sh_bhel_highland",
                "name": "BHEL Township Stadium & Complex",
                "lat": 29.9320,
                "lng": 78.1250,
                "elevation_m": 315,
                "capacity": 60000,
                "type": "Mass Inundation Evacuation Center"
            }
        ],
        "road_network": [
            {
                "id": "rd_koteshwar_ascent",
                "name": "Koteshwar Emergency Hill Road",
                "length_km": 2.5,
                "elevation_m": 620,
                "flood_arrival_min": 999.0,
                "peak_depth_m": 0.0,
                "peak_velocity_ms": 0.0,
                "coordinates": [[30.3380, 78.5150], [30.3450, 78.5220]]
            },
            {
                "id": "rd_devprayag_bridge",
                "name": "Devprayag Sangam Suspension Bridge",
                "length_km": 0.6,
                "elevation_m": 460,
                "flood_arrival_min": 58.0,
                "peak_depth_m": 21.0,
                "peak_velocity_ms": 11.2,
                "coordinates": [[30.1450, 78.5980], [30.1480, 78.6010]]
            },
            {
                "id": "rd_devprayag_cliff",
                "name": "Devprayag Upper Ridge Road",
                "length_km": 2.6,
                "elevation_m": 610,
                "flood_arrival_min": 999.0,
                "peak_depth_m": 0.0,
                "peak_velocity_ms": 0.0,
                "coordinates": [[30.1480, 78.6010], [30.1520, 78.6050]]
            },
            {
                "id": "rd_rishikesh_bypass",
                "name": "Rishikesh - Haridwar Elevated Bypass",
                "length_km": 5.6,
                "elevation_m": 345,
                "flood_arrival_min": 160.0,
                "peak_depth_m": 1.2,
                "peak_velocity_ms": 1.8,
                "coordinates": [[30.0860, 78.2670], [30.0750, 78.2880]]
            },
            {
                "id": "rd_haridwar_nh58",
                "name": "NH-58 Haridwar Ring Expressway",
                "length_km": 8.2,
                "elevation_m": 295,
                "flood_arrival_min": 240.0,
                "peak_depth_m": 0.8,
                "peak_velocity_ms": 0.9,
                "coordinates": [[29.9450, 78.1640], [29.9320, 78.1250]]
            }
        ]
    },
    
    "phuktal_2015": {
        "id": "phuktal_2015",
        "title": "Phuktal River Landslide Lake Outburst (2015)",
        "subtitle": "Natural Rockslide Dam Failure in Glaciated High Altitude Valley",
        "region": "Zanskar Valley, Ladakh, India",
        "event_date": "07 May 2015",
        "dam_type": "Landslide Barrier Dam (60m Height)",
        "location": {"lat": 33.275, "lng": 77.165, "zoom": 12},
        "reservoir": {
            "initial_water_level_m": 3950.0,
            "dam_base_elev_m": 3890.0,
            "dam_height_m": 60.0,
            "crest_elevation_m": 3950.0,
            "max_storage_mcm": 28.0,
            "breach_width_m": 50.0,
            "breach_formation_time_hrs": 0.6,
            "nominal_peak_q_m3s": 9200.0,
            "sediment_concentration_pct": 42.0
        },
        "river_channel": {
            "name": "Tsarap Chu -> Phuktal -> Zanskar River",
            "length_km": 45.0,
            "avg_slope": 0.022,
            "manning_n": 0.060,
            "path_coordinates": [
                [33.2750, 77.1650, 3890], # Dam site
                [33.2680, 77.1850, 3820], # Phuktal Monastery Cliff
                [33.2850, 77.2200, 3740], # Coupling Plane (1.0km)
                [33.3200, 77.2450, 3620], # Marshun Hamlet
                [33.3650, 77.2150, 3510], # Cha Village
                [33.4200, 77.1500, 3400]  # Padum Gateway
            ]
        },
        "settlements": [
            {
                "id": "st_phuktal_gompa",
                "name": "Phuktal Gompa (Ancient Cliff Monastery)",
                "lat": 33.2680,
                "lng": 77.1820,
                "elevation_m": 3850,
                "elevation_diff_m": 40,
                "dist_from_dam_km": 2.2,
                "population": 120,
                "nominal_arrival_time_min": 8.0,
                "nominal_depth_m": 18.2,
                "nominal_velocity_ms": 17.5,
                "buildings_count": 18,
                "schools": 1,
                "hospitals": 0,
                "routes_to_shelters": [
                    {
                        "shelter_id": "sh_phuktal_cave",
                        "distance_km": 0.3,
                        "segment_ids": ["rd_phuktal_cave_stair"],
                        "robustness_pct": 98.0
                    }
                ]
            },
            {
                "id": "st_marshun",
                "name": "Marshun Hamlet",
                "lat": 33.3200,
                "lng": 77.2450,
                "elevation_m": 3620,
                "elevation_diff_m": 270,
                "dist_from_dam_km": 9.5,
                "population": 95,
                "nominal_arrival_time_min": 28.0,
                "nominal_depth_m": 11.5,
                "nominal_velocity_ms": 12.0,
                "buildings_count": 22,
                "schools": 0,
                "hospitals": 0,
                "routes_to_shelters": [
                    {
                        "shelter_id": "sh_cha_highland",
                        "distance_km": 6.5,
                        "segment_ids": ["rd_marshun_footbridge", "rd_marshun_cha"],
                        "robustness_pct": 5.0 # Bridge washed out at T+26m! -> NO VIABLE ROUTE
                    }
                ]
            },
            {
                "id": "st_cha",
                "name": "Cha Village",
                "lat": 33.3650,
                "lng": 77.2150,
                "elevation_m": 3530,
                "elevation_diff_m": 360,
                "dist_from_dam_km": 18.0,
                "population": 340,
                "nominal_arrival_time_min": 52.0,
                "nominal_depth_m": 8.4,
                "nominal_velocity_ms": 9.1,
                "buildings_count": 65,
                "schools": 1,
                "hospitals": 0,
                "routes_to_shelters": [
                    {
                        "shelter_id": "sh_cha_highland",
                        "distance_km": 1.1,
                        "segment_ids": ["rd_cha_ascent"],
                        "robustness_pct": 94.0
                    }
                ]
            },
            {
                "id": "st_padum",
                "name": "Padum Sub-Divisional Center",
                "lat": 33.4200,
                "lng": 77.1500,
                "elevation_m": 3410,
                "elevation_diff_m": 480,
                "dist_from_dam_km": 34.0,
                "population": 2800,
                "nominal_arrival_time_min": 105.0,
                "nominal_depth_m": 4.8,
                "nominal_velocity_ms": 5.6,
                "buildings_count": 480,
                "schools": 3,
                "hospitals": 1,
                "routes_to_shelters": [
                    {
                        "shelter_id": "sh_padum_cantt",
                        "distance_km": 2.5,
                        "segment_ids": ["rd_padum_artery"],
                        "robustness_pct": 99.0
                    }
                ]
            }
        ],
        "shelters": [
            {
                "id": "sh_phuktal_cave",
                "name": "Phuktal Sacred Limestone Cave Safe Sanctuary",
                "lat": 33.2670,
                "lng": 77.1810,
                "elevation_m": 3920,
                "capacity": 250,
                "type": "Natural Elevated Cliff Cave"
            },
            {
                "id": "sh_cha_highland",
                "name": "Cha Upper Pasture Staging Camp",
                "lat": 33.3680,
                "lng": 77.2180,
                "elevation_m": 3720,
                "capacity": 800,
                "type": "Terrace Relief Camp"
            },
            {
                "id": "sh_padum_cantt",
                "name": "Padum District Administration Safe Complex",
                "lat": 33.4250,
                "lng": 77.1420,
                "elevation_m": 3520,
                "capacity": 4500,
                "type": "Permanent Civil Center"
            }
        ],
        "road_network": [
            {
                "id": "rd_phuktal_cave_stair",
                "name": "Monastery Vertical Cliff Steps",
                "length_km": 0.3,
                "elevation_m": 3900,
                "flood_arrival_min": 999.0,
                "peak_depth_m": 0.0,
                "peak_velocity_ms": 0.0,
                "coordinates": [[33.2680, 77.1820], [33.2670, 77.1810]]
            },
            {
                "id": "rd_marshun_footbridge",
                "name": "Marshun Tsarap Wooden Suspension Bridge",
                "length_km": 0.2,
                "elevation_m": 3625,
                "flood_arrival_min": 26.0,
                "peak_depth_m": 11.5,
                "peak_velocity_ms": 12.0,
                "coordinates": [[33.3200, 77.2450], [33.3220, 77.2430]]
            },
            {
                "id": "rd_marshun_cha",
                "name": "River Gorge Mule Track (Marshun - Cha)",
                "length_km": 6.3,
                "elevation_m": 3580,
                "flood_arrival_min": 35.0,
                "peak_depth_m": 8.0,
                "peak_velocity_ms": 10.0,
                "coordinates": [[33.3220, 77.2430], [33.3650, 77.2150]]
            },
            {
                "id": "rd_cha_ascent",
                "name": "Cha Upper Ridge Track",
                "length_km": 1.1,
                "elevation_m": 3680,
                "flood_arrival_min": 999.0,
                "peak_depth_m": 0.0,
                "peak_velocity_ms": 0.0,
                "coordinates": [[33.3650, 77.2150], [33.3680, 77.2180]]
            },
            {
                "id": "rd_padum_artery",
                "name": "Padum Elevated Highway",
                "length_km": 2.5,
                "elevation_m": 3490,
                "flood_arrival_min": 999.0,
                "peak_depth_m": 0.0,
                "peak_velocity_ms": 0.0,
                "coordinates": [[33.4200, 77.1500], [33.4250, 77.1420]]
            }
        ]
    }
}
