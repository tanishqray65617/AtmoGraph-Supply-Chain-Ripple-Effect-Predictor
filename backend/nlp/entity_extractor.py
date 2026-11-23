"""
AtmoGraph NLP Named Entity Recognition & Disruption Assessment Pipeline
======================================================================
Author: Tanishq Ray <tanishqray65617@gmail.com>
Description: Parses unstructured maritime, transport, and geopolitical incident
  reports using spaCy NER and rule-based ontology matching to identify:
  1. Affected supply chain entities (Ports, Suppliers, Manufacturers, Transit Hubs)
  2. Geographic locations (GPE/LOC)
  3. Incident category (Strike, Natural Hazard, Regulatory, Hardware Failure)
  4. Initial Shock Severity Index (0.0 to 1.0 scale)
"""

import logging
import re
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

DISRUPTION_KEYWORDS = {
    "Labor Strike": [r"strike", r"dockworker", r"walkout", r"labor dispute", r"protest", r"union boycott"],
    "Natural Hazard": [r"typhoon", r"earthquake", r"cyclone", r"hurricane", r"flooding", r"tsunami", r"blizzard"],
    "Infrastructure Failure": [r"power grid", r"blackout", r"derailment", r"fire", r"explosion", r"pipeline burst"],
    "Geopolitical Crisis": [r"sanction", r"embargo", r"blockade", r"tariff", r"customs dispute", r"war", r"conflict"],
    "Regulatory Compliance": [r"inspection backlog", r"safety audit", r"regulatory overhaul", r"import ban"]
}

SEVERITY_WEIGHTS = {
    "Natural Hazard": 0.90,
    "Labor Strike": 0.85,
    "Geopolitical Crisis": 0.88,
    "Infrastructure Failure": 0.75,
    "Regulatory Compliance": 0.55
}

class DisruptionEntityExtractor:
    def __init__(self, model_name: str = "en_core_web_sm"):
        self.nlp = None
        try:
            import spacy
            self.nlp = spacy.load(model_name)
            logger.info(f"Loaded spaCy NER model: {model_name}")
        except Exception as e:
            logger.warning(f"spaCy model {model_name} not installed locally. Falling back to regex-based NER extraction: {e}")

    def extract(self, text: str, known_entities: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Extract named entities, classify disruption type, and score severity.
        """
        entities = []
        matched_node_ids = []

        # 1. spaCy NER (if available)
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ in ["GPE", "LOC", "ORG", "FAC"]:
                    entities.append({
                        "text": ent.text,
                        "label": ent.label_,
                        "start_char": ent.start_char,
                        "end_char": ent.end_char
                    })

        # 2. Known Supply Chain Entity Matching (Fallback + Accuracy Booster)
        if known_entities:
            text_lower = text.lower()
            for node in known_entities:
                name = node.get("name", "")
                location = node.get("location", "")
                if name and name.lower() in text_lower:
                    matched_node_ids.append({
                        "id": node.get("id"),
                        "name": name,
                        "type": node.get("type"),
                        "location": location,
                        "confidence": 0.98
                    })
                elif location and re.search(rf"\b{re.escape(location.lower())}\b", text_lower):
                    matched_node_ids.append({
                        "id": node.get("id"),
                        "name": name,
                        "type": node.get("type"),
                        "location": location,
                        "confidence": 0.75
                    })

        # 3. Disruption Type Classification
        classified_type = "Unspecified Incident"
        severity = 0.50

        for category, patterns in DISRUPTION_KEYWORDS.items():
            for pat in patterns:
                if re.search(pat, text, re.IGNORECASE):
                    classified_type = category
                    severity = SEVERITY_WEIGHTS.get(category, 0.65)
                    break
            if classified_type != "Unspecified Incident":
                break

        # Extract numerical mentions of delays (e.g., "14 days", "surge past 18 days")
        delay_match = re.search(r"(\d+)\s*(?:-|to)?\s*(\d+)?\s*(?:day|days)", text, re.IGNORECASE)
        estimated_delay_days = 14.0
        if delay_match:
            try:
                days_val = float(delay_match.group(1))
                estimated_delay_days = days_val
            except Exception:
                pass

        return {
            "text": text,
            "disruption_type": classified_type,
            "severity_index": severity,
            "estimated_delay_days": estimated_delay_days,
            "spacy_entities": entities,
            "matched_nodes": matched_node_ids,
            "is_actionable": len(matched_node_ids) > 0
        }

# Global singleton extractor instance
nlp_extractor = DisruptionEntityExtractor()

