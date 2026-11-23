#!/usr/bin/env python3
"""
AtmoGraph Procedural Supply Chain Dataset Generator
===================================================
Author: Tanishq Ray <tanishqray65617@gmail.com>
Description: Generates realistic global supply chain multi-tier graph data:
  - nodes.json: RawMaterialSuppliers, Manufacturers, Ports, DistributionCenters, Retailers
  - edges.json: SUPPLIES_TO, SHIPS_THROUGH dependency edges with lead times & volumes
  - news.json: Disruption incident alerts simulating real-world supply chain crises
  - supply_chain_data.json: Combined unified dataset format for rapid graph ingest
"""

import json
import random
import os
from typing import Dict, List, Any

# Ensure reproducible mock datasets
random.seed(42)

NODE_TYPES = [
    "RawMaterialSupplier",
    "Manufacturer",
    "Port",
    "DistributionCenter",
    "Retailer"
]

LOCATIONS = [
    {"city": "Rotterdam", "country": "Netherlands", "lat": 51.9244, "lng": 4.4777},
    {"city": "Shanghai", "country": "China", "lat": 31.2304, "lng": 121.4737},
    {"city": "Singapore", "country": "Singapore", "lat": 1.3521, "lng": 103.8198},
    {"city": "Los Angeles", "country": "USA", "lat": 34.0522, "lng": -118.2437},
    {"city": "Hamburg", "country": "Germany", "lat": 53.5511, "lng": 9.9937},
    {"city": "Busan", "country": "South Korea", "lat": 35.1796, "lng": 129.0756},
    {"city": "Kaohsiung", "country": "Taiwan", "lat": 22.6273, "lng": 120.3014},
    {"city": "Antwerp", "country": "Belgium", "lat": 51.2194, "lng": 4.4025},
    {"city": "Tokyo", "country": "Japan", "lat": 35.6762, "lng": 139.6503},
    {"city": "Detroit", "country": "USA", "lat": 42.3314, "lng": -83.0458},
    {"city": "Stuttgart", "country": "Germany", "lat": 48.7758, "lng": 9.1829},
    {"city": "Shenzhen", "country": "China", "lat": 22.5431, "lng": 114.0579},
    {"city": "Austin", "country": "USA", "lat": 30.2672, "lng": -97.7431},
    {"city": "Yokohama", "country": "Japan", "lat": 35.4437, "lng": 139.6380},
    {"city": "Dubai", "country": "UAE", "lat": 25.2048, "lng": 55.2708},
    {"city": "Felixstowe", "country": "UK", "lat": 51.9634, "lng": 1.3512},
    {"city": "Chicago", "country": "USA", "lat": 41.8781, "lng": -87.6298},
    {"city": "Munich", "country": "Germany", "lat": 48.1351, "lng": 11.5820},
    {"city": "Bengaluru", "country": "India", "lat": 12.9716, "lng": 77.5946},
    {"city": "Guangzhou", "country": "China", "lat": 23.1291, "lng": 113.2644}
]

INDUSTRY_SECTORS = ["Semiconductors", "Automotive", "Pharmaceuticals", "Renewable Energy", "Aerospace"]

RAW_SUPPLIERS = [
    ("Nordic Lithium Mining Ltd", "Rotterdam", "RawMaterialSupplier", "Renewable Energy"),
    ("Pacific Rare Earth Corp", "Shanghai", "RawMaterialSupplier", "Semiconductors"),
    ("Taiwan Silicon Ingot Labs", "Kaohsiung", "RawMaterialSupplier", "Semiconductors"),
    ("Bavaria High-Grade Steel AG", "Stuttgart", "RawMaterialSupplier", "Automotive"),
    ("Nippon Polymer Synthetics", "Tokyo", "RawMaterialSupplier", "Pharmaceuticals"),
    ("Texas Petrochemical Precursors", "Austin", "RawMaterialSupplier", "Automotive"),
    ("SinoChemical Special Materials", "Shenzhen", "RawMaterialSupplier", "Semiconductors"),
    ("Scania Precision Castings", "Hamburg", "RawMaterialSupplier", "Aerospace"),
    ("Hanseatic Industrial Gases", "Antwerp", "RawMaterialSupplier", "Pharmaceuticals"),
    ("Gobi Cobalt Refining Co", "Shanghai", "RawMaterialSupplier", "Renewable Energy")
]

PORTS = [
    ("Port of Rotterdam", "Rotterdam", "Port"),
    ("Port of Shanghai", "Shanghai", "Port"),
    ("Port of Singapore", "Singapore", "Port"),
    ("Port of Los Angeles", "Los Angeles", "Port"),
    ("Port of Hamburg", "Hamburg", "Port"),
    ("Port of Busan", "Busan", "Port"),
    ("Port of Kaohsiung", "Kaohsiung", "Port"),
    ("Port of Antwerp", "Antwerp", "Port"),
    ("Port of Felixstowe", "Felixstowe", "Port"),
    ("Port of Dubai", "Dubai", "Port")
]

MANUFACTURERS = [
    ("Apex Microelectronics Fab", "Shenzhen", "Manufacturer", "Semiconductors"),
    ("Continental Powertrain Assembly", "Munich", "Manufacturer", "Automotive"),
    ("Silicon Valley Processor Systems", "Austin", "Manufacturer", "Semiconductors"),
    ("Nippon Precision Optics", "Yokohama", "Manufacturer", "Aerospace"),
    ("EuroPharma Bio-Synthetics", "Antwerp", "Manufacturer", "Pharmaceuticals"),
    ("Midwest Electric Drive Tech", "Detroit", "Manufacturer", "Automotive"),
    ("Shenzhen Advanced Display Corp", "Shenzhen", "Manufacturer", "Semiconductors"),
    ("Rhineland Robotic Modules", "Stuttgart", "Manufacturer", "Automotive"),
    ("Hokkaido Sensor Fabricators", "Tokyo", "Manufacturer", "Aerospace"),
    ("Bharat Semiconductor Foundry", "Bengaluru", "Manufacturer", "Semiconductors")
]

DIST_CENTERS = [
    ("Western Europe Mega-Hub DC", "Rotterdam", "DistributionCenter"),
    ("East Asia Central Consolidation", "Shanghai", "DistributionCenter"),
    ("North American Heartland Logistics", "Chicago", "DistributionCenter"),
    ("Southern California Gateway DC", "Los Angeles", "DistributionCenter"),
    ("Central European Fulfillment Hub", "Hamburg", "DistributionCenter"),
    ("ASEAN Strategic Freight Center", "Singapore", "DistributionCenter"),
    ("Texas Regional Depot", "Austin", "DistributionCenter"),
    ("UK Southern Logistics Facility", "Felixstowe", "DistributionCenter"),
    ("Great Lakes Distribution Center", "Detroit", "DistributionCenter"),
    ("Middle East Crossdock Center", "Dubai", "DistributionCenter")
]

RETAILERS = [
    ("HyperTech Electronics Retail", "Chicago", "Retailer"),
    ("Global Auto Dealership Alliance", "Detroit", "Retailer"),
    ("MedCare Health Distribution", "Munich", "Retailer"),
    ("VoltMotion EV Showrooms", "Austin", "Retailer"),
    ("EuroConsumer Superstores", "Hamburg", "Retailer"),
    ("Pacific Coast Retail Network", "Los Angeles", "Retailer"),
    ("Nordic Appliance Outlets", "Rotterdam", "Retailer"),
    ("East Asia Direct Commerce", "Tokyo", "Retailer"),
    ("SingaMart Digital Fulfillment", "Singapore", "Retailer"),
    ("Britannia Retail Syndicate", "Felixstowe", "Retailer")
]

NEWS_TEMPLATES = [
    {
        "headline": "Dockworker Strike Shuts Down Maritime Terminals at Port of Rotterdam",
        "content": "A sudden labor dispute and union strike has paralyzed cargo unloading at the Port of Rotterdam. Container dwell times have surged past 14 days, threatening European raw material deliveries.",
        "target_entity": "Port of Rotterdam",
        "severity": 0.85,
        "disruption_type": "Labor Strike",
        "estimated_delay_days": 18
    },
    {
        "headline": "Super Typhoon In-fa Forces Complete Closure of Port of Shanghai",
        "content": "Category 4 winds and coastal flooding have prompted port authorities to suspend all vessel berths at the Port of Shanghai. Supply chains dependent on outbound electronics components face immediate freezes.",
        "target_entity": "Port of Shanghai",
        "severity": 0.92,
        "disruption_type": "Natural Hazard",
        "estimated_delay_days": 21
    },
    {
        "headline": "Power Grid Failure Halts Production at Apex Microelectronics Fab in Shenzhen",
        "content": "An unexpected thermal power plant shutdown across the industrial zone has suspended cleanroom operations at Apex Microelectronics Fab, constraining microchip wafer supplies for global automakers.",
        "target_entity": "Apex Microelectronics Fab",
        "severity": 0.78,
        "disruption_type": "Infrastructure Failure",
        "estimated_delay_days": 14
    },
    {
        "headline": "Rail Freight Derailment Bottlenecks North American Heartland Logistics in Chicago",
        "content": "A major freight train derailment on the Midwest corridor has severed intermodal connectivity into North American Heartland Logistics, causing inter-state distribution delays.",
        "target_entity": "North American Heartland Logistics",
        "severity": 0.65,
        "disruption_type": "Logistics Route Obstruction",
        "estimated_delay_days": 9
    },
    {
        "headline": "Customs Regulatory Overhaul Delays Chemical Shipments at Port of Hamburg",
        "content": "New European chemical safety verification protocols have created severe container inspection backlogs at the Port of Hamburg, impacting pharmaceutical precursor supplies.",
        "target_entity": "Port of Hamburg",
        "severity": 0.55,
        "disruption_type": "Regulatory Compliance",
        "estimated_delay_days": 12
    },
    {
        "headline": "Earthquake Aftershocks Trigger Precautionary Shutdown at Nippon Precision Optics",
        "content": "Following seismic activity in Kanagawa prefecture, safety diagnostics are underway at Nippon Precision Optics, pausing precision optical component assembly for defense and aerospace contractors.",
        "target_entity": "Nippon Precision Optics",
        "severity": 0.70,
        "disruption_type": "Natural Hazard",
        "estimated_delay_days": 15
    }
]

def generate_dataset() -> Dict[str, Any]:
    nodes = []
    edges = []
    node_id_counter = 1
    node_lookup = {}

    loc_dict = {loc["city"]: loc for loc in LOCATIONS}

    # 1. Generate RawMaterialSuppliers
    supplier_ids = []
    for name, city, n_type, sector in RAW_SUPPLIERS:
        loc = loc_dict.get(city, LOCATIONS[0])
        nid = f"SUP-{node_id_counter:03d}"
        node_id_counter += 1
        node_obj = {
            "id": nid,
            "name": name,
            "type": n_type,
            "sector": sector,
            "location": city,
            "country": loc["country"],
            "latitude": loc["lat"],
            "longitude": loc["lng"],
            "base_risk_score": 0.0,
            "capacity_tonnes": random.randint(15000, 60000),
            "criticality_tier": random.choice([1, 2])
        }
        nodes.append(node_obj)
        supplier_ids.append(nid)
        node_lookup[name] = nid

    # 2. Generate Ports
    port_ids = []
    for name, city, n_type in PORTS:
        loc = loc_dict.get(city, LOCATIONS[0])
        nid = f"PRT-{node_id_counter:03d}"
        node_id_counter += 1
        node_obj = {
            "id": nid,
            "name": name,
            "type": n_type,
            "sector": "Maritime Logistics",
            "location": city,
            "country": loc["country"],
            "latitude": loc["lat"],
            "longitude": loc["lng"],
            "base_risk_score": 0.0,
            "capacity_teu_per_year": random.randint(3000000, 35000000),
            "criticality_tier": 1
        }
        nodes.append(node_obj)
        port_ids.append(nid)
        node_lookup[name] = nid

    # 3. Generate Manufacturers
    manufacturer_ids = []
    for name, city, n_type, sector in MANUFACTURERS:
        loc = loc_dict.get(city, LOCATIONS[0])
        nid = f"MFG-{node_id_counter:03d}"
        node_id_counter += 1
        node_obj = {
            "id": nid,
            "name": name,
            "type": n_type,
            "sector": sector,
            "location": city,
            "country": loc["country"],
            "latitude": loc["lat"],
            "longitude": loc["lng"],
            "base_risk_score": 0.0,
            "annual_output_units": random.randint(50000, 1000000),
            "criticality_tier": random.choice([1, 2, 3])
        }
        nodes.append(node_obj)
        manufacturer_ids.append(nid)
        node_lookup[name] = nid

    # 4. Generate Distribution Centers
    dist_ids = []
    for name, city, n_type in DIST_CENTERS:
        loc = loc_dict.get(city, LOCATIONS[0])
        nid = f"DC-{node_id_counter:03d}"
        node_id_counter += 1
        node_obj = {
            "id": nid,
            "name": name,
            "type": n_type,
            "sector": "Fulfillment & Warehousing",
            "location": city,
            "country": loc["country"],
            "latitude": loc["lat"],
            "longitude": loc["lng"],
            "base_risk_score": 0.0,
            "warehouse_sqft": random.randint(200000, 1500000),
            "criticality_tier": 2
        }
        nodes.append(node_obj)
        dist_ids.append(nid)
        node_lookup[name] = nid

    # 5. Generate Retailers
    retail_ids = []
    for name, city, n_type in RETAILERS:
        loc = loc_dict.get(city, LOCATIONS[0])
        nid = f"RET-{node_id_counter:03d}"
        node_id_counter += 1
        node_obj = {
            "id": nid,
            "name": name,
            "type": n_type,
            "sector": "Consumer End-Market",
            "location": city,
            "country": loc["country"],
            "latitude": loc["lat"],
            "longitude": loc["lng"],
            "base_risk_score": 0.0,
            "annual_revenue_usd_m": random.randint(50, 850),
            "criticality_tier": 3
        }
        nodes.append(node_obj)
        retail_ids.append(nid)
        node_lookup[name] = nid

    # --- Edge Generation ---
    edge_id_counter = 1

    # Tier 1 -> Port (Supplier to Port)
    for sup_id in supplier_ids:
        assigned_ports = random.sample(port_ids, k=random.randint(1, 2))
        for p_id in assigned_ports:
            edges.append({
                "id": f"E-{edge_id_counter:04d}",
                "source": sup_id,
                "target": p_id,
                "type": "SHIPS_THROUGH",
                "lead_time_days": random.randint(3, 8),
                "volume": round(random.uniform(500.0, 5000.0), 2),
                "reliability_score": round(random.uniform(0.85, 0.99), 3),
                "criticality": random.choice(["MEDIUM", "HIGH"])
            })
            edge_id_counter += 1

    # Port -> Manufacturer
    for mfg_id in manufacturer_ids:
        inbound_ports = random.sample(port_ids, k=random.randint(2, 3))
        for p_id in inbound_ports:
            edges.append({
                "id": f"E-{edge_id_counter:04d}",
                "source": p_id,
                "target": mfg_id,
                "type": "SUPPLIES_TO",
                "lead_time_days": random.randint(10, 28),
                "volume": round(random.uniform(1000.0, 10000.0), 2),
                "reliability_score": round(random.uniform(0.80, 0.98), 3),
                "criticality": random.choice(["HIGH", "CRITICAL"])
            })
            edge_id_counter += 1

    # Direct Supplier -> Manufacturer (local component feeds)
    for i, sup_id in enumerate(supplier_ids):
        target_mfg = manufacturer_ids[i % len(manufacturer_ids)]
        edges.append({
            "id": f"E-{edge_id_counter:04d}",
            "source": sup_id,
            "target": target_mfg,
            "type": "SUPPLIES_TO",
            "lead_time_days": random.randint(2, 7),
            "volume": round(random.uniform(800.0, 4000.0), 2),
            "reliability_score": round(random.uniform(0.90, 0.99), 3),
            "criticality": "HIGH"
        })
        edge_id_counter += 1

    # Manufacturer -> Distribution Center
    for mfg_id in manufacturer_ids:
        target_dcs = random.sample(dist_ids, k=random.randint(2, 3))
        for dc_id in target_dcs:
            edges.append({
                "id": f"E-{edge_id_counter:04d}",
                "source": mfg_id,
                "target": dc_id,
                "type": "SUPPLIES_TO",
                "lead_time_days": random.randint(5, 14),
                "volume": round(random.uniform(2000.0, 15000.0), 2),
                "reliability_score": round(random.uniform(0.88, 0.99), 3),
                "criticality": "HIGH"
            })
            edge_id_counter += 1

    # Distribution Center -> Retailer
    for dc_id in dist_ids:
        target_retailers = random.sample(retail_ids, k=random.randint(2, 4))
        for ret_id in target_retailers:
            edges.append({
                "id": f"E-{edge_id_counter:04d}",
                "source": dc_id,
                "target": ret_id,
                "type": "SUPPLIES_TO",
                "lead_time_days": random.randint(1, 5),
                "volume": round(random.uniform(500.0, 8000.0), 2),
                "reliability_score": round(random.uniform(0.92, 0.99), 3),
                "criticality": "MEDIUM"
            })
            edge_id_counter += 1

    # Enhance news events with mapped node IDs
    enhanced_news = []
    for item in NEWS_TEMPLATES:
        mapped_id = node_lookup.get(item["target_entity"])
        enhanced_news.append({
            "id": f"NEWS-{random.randint(1000, 9999)}",
            "headline": item["headline"],
            "content": item["content"],
            "target_entity": item["target_entity"],
            "target_node_id": mapped_id,
            "disruption_type": item["disruption_type"],
            "severity_index": item["severity"],
            "estimated_delay_days": item["estimated_delay_days"],
            "timestamp": "2026-11-10T08:00:00Z"
        })

    return {
        "metadata": {
            "version": "1.0.0",
            "generator": "AtmoGraph Mock Data Engine",
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "total_news_items": len(enhanced_news)
        },
        "nodes": nodes,
        "edges": edges,
        "news": enhanced_news
    }

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)

    dataset = generate_dataset()

    # Save individual JSON files as requested in product.md
    nodes_path = os.path.join(data_dir, "nodes.json")
    edges_path = os.path.join(data_dir, "edges.json")
    news_path = os.path.join(data_dir, "news.json")
    unified_path = os.path.join(data_dir, "supply_chain_data.json")

    with open(nodes_path, "w", encoding="utf-8") as f:
        json.dump(dataset["nodes"], f, indent=2)

    with open(edges_path, "w", encoding="utf-8") as f:
        json.dump(dataset["edges"], f, indent=2)

    with open(news_path, "w", encoding="utf-8") as f:
        json.dump(dataset["news"], f, indent=2)

    with open(unified_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2)

    print(f"Generated {len(dataset['nodes'])} nodes saved to {nodes_path}")
    print(f"Generated {len(dataset['edges'])} edges saved to {edges_path}")
    print(f"Generated {len(dataset['news'])} news items saved to {news_path}")
    print(f"Unified dataset saved to {unified_path}")

if __name__ == "__main__":
    main()

