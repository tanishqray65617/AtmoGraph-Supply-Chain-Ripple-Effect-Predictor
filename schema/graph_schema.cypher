// ============================================================================
// AtmoGraph Cypher Graph Schema Definition
// Version: 1.0.0
// Description: Multi-tier global supply chain ontology, constraints, and indexes
// ============================================================================

// ----------------------------------------------------------------------------
// 1. Uniqueness Constraints & Primary Keys
// ----------------------------------------------------------------------------

CREATE CONSTRAINT unique_supplier_id IF NOT EXISTS
FOR (s:RawMaterialSupplier) REQUIRE s.id IS UNIQUE;

CREATE CONSTRAINT unique_manufacturer_id IF NOT EXISTS
FOR (m:Manufacturer) REQUIRE m.id IS UNIQUE;

CREATE CONSTRAINT unique_distribution_center_id IF NOT EXISTS
FOR (dc:DistributionCenter) REQUIRE dc.id IS UNIQUE;

CREATE CONSTRAINT unique_retailer_id IF NOT EXISTS
FOR (r:Retailer) REQUIRE r.id IS UNIQUE;

CREATE CONSTRAINT unique_port_id IF NOT EXISTS
FOR (p:Port) REQUIRE p.id IS UNIQUE;

// ----------------------------------------------------------------------------
// 2. Performance Indexes on Critical Search Attributes
// ----------------------------------------------------------------------------

CREATE INDEX idx_supplier_name IF NOT EXISTS
FOR (s:RawMaterialSupplier) ON (s.name);

CREATE INDEX idx_port_name IF NOT EXISTS
FOR (p:Port) ON (p.name);

CREATE INDEX idx_node_location IF NOT EXISTS
FOR (n:SupplyNode) ON (n.location);

CREATE INDEX idx_node_risk IF NOT EXISTS
FOR (n:SupplyNode) ON (n.risk_score);

// ----------------------------------------------------------------------------
// 3. Schema Documentation & Node Metatypes
// ----------------------------------------------------------------------------
// Node Labels:
//   (:SupplyNode)                - Base abstract label for all supply chain entities
//   (:RawMaterialSupplier)       - Extraction & processing facilities (metals, chips, chemicals)
//   (:Manufacturer)              - Assembly & fabrication facilities
//   (:DistributionCenter)        - Regional sorting & logistics hubs
//   (:Retailer)                  - Point of consumer fulfillment
//   (:Port)                      - Deep-sea maritime container ports and air transit hubs
//
// Relationship Types:
//   [:SUPPLIES_TO {lead_time_days: Int, volume: Float, reliability_score: Float}]
//   [:SHIPS_THROUGH {lead_time_days: Int, customs_delay_buffer: Int, active_status: Boolean}]
//   [:CONNECTS_TO {transit_days: Int, mode: String, capacity_utilization: Float}]
// ----------------------------------------------------------------------------

