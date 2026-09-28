#!/usr/bin/env python3
"""
BLOON WAR GAMES: SOVEREIGNTY & DIPLOMACY v0.1.2f
Indonesian Maritime Exercise Simulator — Educational Game
INITIALIZATION FIX
"""

import pygame
import sys
import math
import random
import array
import os

# ═══════════════════════════════════════════════════════════
# SECTION 1 — CONSTANTS & CONFIG
# ═══════════════════════════════════════════════════════════
W, H = 1280, 720
FPS = 30

STAT_KEYS = ("readiness", "tension", "safety", "trust", "legal")

PLAN_X = 815
PLAN_EX_Y = 90
PLAN_LOC_Y = 270
PLAN_PART_X = 1045
PLAN_PART_Y = 90
PLAN_ROW_H = 19
PLAN_BTN_W = 210
PLAN_BTN_H = 18

C_BG        = (10, 14, 26)
C_PANEL     = (16, 22, 40)
C_BORDER    = (0, 200, 180)
C_TEXT      = (200, 220, 230)
C_DIM       = (100, 120, 140)
C_ACCENT    = (0, 255, 200)
C_WARN      = (255, 180, 0)
C_DANGER    = (255, 60, 60)
C_GOOD      = (60, 255, 120)
C_OCEAN     = (8, 18, 48)
C_LAND      = (30, 80, 50)
C_LAND2     = (40, 95, 55)
C_GRID      = (20, 40, 60)
C_INTERNAL  = (20, 50, 120)
C_ARCH      = (25, 60, 130)
C_TERR      = (30, 75, 145)
C_CONTIG    = (35, 90, 155)
C_EEZ       = (20, 70, 130)
C_SHELF     = (15, 55, 110)
C_HIGH      = (8, 18, 48)
C_BTN       = (20, 50, 70)
C_BTN_HOV   = (30, 80, 110)
C_BTN_ACT   = (0, 160, 140)

ZONE_COLORS = {
    "internal": C_INTERNAL,
    "archipelagic": C_ARCH,
    "territorial": C_TERR,
    "contiguous": C_CONTIG,
    "eez": C_EEZ,
    "shelf": C_SHELF,
    "high": C_HIGH,
}

# ═══════════════════════════════════════════════════════════
# SECTION 2 — SOUND SYSTEM
# ═══════════════════════════════════════════════════════════
SOUND_ENABLED = True
SND = {}


def _make_tone(freq, dur, vol=0.15):
    sr = 22050
    n = int(sr * dur)
    buf = array.array('h', [0] * n)
    for i in range(n):
        env = 1.0 - (i / n)
        buf[i] = int(vol * 32767 * env * math.sin(2 * math.pi * freq * i / sr))
    return pygame.mixer.Sound(buffer=buf)


def init_sounds():
    global SND
    try:
        pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
        SND["click"] = _make_tone(800, 0.06, 0.12)
        SND["ping"] = _make_tone(1200, 0.15, 0.10)
        SND["warn"] = _make_tone(440, 0.3, 0.15)
        SND["success"] = _make_tone(660, 0.4, 0.12)
        SND["alert"] = _make_tone(330, 0.5, 0.18)
    except Exception:
        pass


def play(name):
    if SOUND_ENABLED and name in SND:
        try:
            SND[name].play()
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════
# SECTION 3 — DATA: COUNTRIES & ZONES
# ═══════════════════════════════════════════════════════════
COUNTRIES = [
    {"id": "ID", "name": "Indonesia", "asean": True},
    {"id": "AU", "name": "Australia", "asean": False},
    {"id": "SG", "name": "Singapore", "asean": True},
    {"id": "MY", "name": "Malaysia", "asean": True},
    {"id": "JP", "name": "Japan", "asean": False},
    {"id": "US", "name": "United States", "asean": False},
    {"id": "IN", "name": "India", "asean": False},
    {"id": "KR", "name": "South Korea", "asean": False},
    {"id": "NZ", "name": "New Zealand", "asean": False},
    {"id": "PH", "name": "Philippines", "asean": True},
]
COUNTRY_MAP = {c["id"]: c for c in COUNTRIES}

ZONES = {
    "internal": {
        "name": "Internal Waters (Perairan Pedalaman)",
        "sovereignty": "Full Sovereignty",
        "navigation": "Passage is generally subject to the coastal State's jurisdiction, subject to applicable UNCLOS exceptions.",
        "complexity": "LOW",
        "desc": "Waters landward of the baseline. Full sovereignty applies, identical to land territory.",
        "legal": "LEGAL RULE — UNCLOS Art. 8"
    },
    "archipelagic": {
        "name": "Archipelagic Waters (Perairan Kepulauan)",
        "sovereignty": "Full Sovereignty",
        "navigation": "Innocent Passage + Archipelagic Sea Lanes Passage (ALKI).",
        "complexity": "MEDIUM",
        "desc": "Waters enclosed by archipelagic baselines. Sovereignty applies, but ALKI transit rights must be respected.",
        "legal": "LEGAL RULE — UNCLOS Part IV, Art. 49-54"
    },
    "territorial": {
        "name": "Territorial Sea (Laut Teritorial)",
        "sovereignty": "Full Sovereignty",
        "navigation": "Foreign ships may exercise innocent passage through the territorial sea when the passage meets the applicable legal conditions.",
        "complexity": "MEDIUM",
        "desc": "Up to 12 NM. Full sovereignty including airspace/seabed. Foreign ships may exercise innocent passage if continuous and expeditious.",
        "legal": "LEGAL RULE — UNCLOS Part II, Art. 2-3, 17-19"
    },
    "contiguous": {
        "name": "Contiguous Zone (Zona Tambahan)",
        "sovereignty": "No",
        "navigation": "Freedom of Navigation. Coastal state has limited jurisdiction.",
        "complexity": "LOW",
        "desc": "Up to 24 NM. Not sovereign territory. Indonesia may enforce customs, fiscal, immigration, and sanitary laws.",
        "legal": "LEGAL RULE — UNCLOS Art. 33"
    },
    "eez": {
        "name": "Exclusive Economic Zone (ZEE)",
        "sovereignty": "No — NOT sovereign territory",
        "navigation": "Freedom of Navigation & Overflight. Military activities involve differing State practices.",
        "complexity": "HIGH — DISPUTED INTERPRETATION",
        "desc": "Up to 200 NM. Indonesia has SOVEREIGN RIGHTS over resources, NOT sovereignty. Military activities in an EEZ involve differing State practices; this simulation does not resolve every such dispute.",
        "legal": "DISPUTED INTERPRETATION — UNCLOS Art. 56, 58, Due Regard Principle"
    },
    "shelf": {
        "name": "Continental Shelf (Landas Kontinen)",
        "sovereignty": "No",
        "navigation": "Does not affect water column status above.",
        "complexity": "MEDIUM",
        "desc": "Seabed/subsoil to 200 NM (or 350 NM). Sovereign rights over seabed resources only.",
        "legal": "LEGAL RULE — UNCLOS Part VI, Art. 76-77"
    },
    "high": {
        "name": "High Seas (Laut Lepas)",
        "sovereignty": "No — Res Communis (Freedom of the High Seas)",
        "navigation": "Full Freedom of Navigation, Overflight, Fishing, Research.",
        "complexity": "LOW",
        "desc": "Beyond any national EEZ. Open to all states. NOTE: 'Common Heritage of Mankind' applies to 'The Area' (seabed beyond national jurisdiction), NOT the High Seas water column.",
        "legal": "LEGAL RULE — UNCLOS Part VII (High Seas) & Part XI (The Area)"
    },
}

# ═══════════════════════════════════════════════════════════
# SECTION 4 — DATA: EXERCISES, LOCATIONS, MISSIONS
# ═══════════════════════════════════════════════════════════
EXERCISE_TYPES = [
    {"id": "combat", "name": "Combat Readiness", "readiness": 15, "tension": 10, "safety": -5, "trust": -3, "legal_risk": 3},
    {"id": "marsec", "name": "Maritime Security", "readiness": 8, "tension": 2, "safety": 3, "trust": 5, "legal_risk": 1},
    {"id": "sar", "name": "Search & Rescue (SAR)", "readiness": 5, "tension": -5, "safety": 5, "trust": 10, "legal_risk": 0},
    {"id": "hadr", "name": "HADR", "readiness": 3, "tension": -8, "safety": 5, "trust": 15, "legal_risk": 0},
    {"id": "med", "name": "Military Medicine", "readiness": 5, "tension": -3, "safety": 5, "trust": 8, "legal_risk": 0},
    {"id": "peace", "name": "Peacekeeping Prep", "readiness": 8, "tension": -2, "safety": 3, "trust": 10, "legal_risk": 1},
    {"id": "asw", "name": "Anti-Submarine Warfare", "readiness": 12, "tension": 15, "safety": -8, "trust": -5, "legal_risk": 10},
    {"id": "livefire", "name": "Live Fire Exercise", "readiness": 15, "tension": 8, "safety": -15, "trust": -2, "legal_risk": 5},
]
EX_MAP = {e["id"]: e for e in EXERCISE_TYPES}

LOCATIONS = [
    {"id": "java_sea", "name": "Java Sea", "zone": "archipelagic"},
    {"id": "natuna", "name": "North Natuna Sea", "zone": "eez"},
    {"id": "makassar", "name": "Makassar Strait", "zone": "archipelagic"},
    {"id": "arafura", "name": "Arafura Sea", "zone": "eez"},
    {"id": "indian", "name": "Indian Ocean (South)", "zone": "eez"},
    {"id": "pacific", "name": "Pacific Ocean (North)", "zone": "eez"},
    {"id": "internal_jv", "name": "Internal Waters (Java)", "zone": "internal"},
    {"id": "terr_sing", "name": "Territorial Sea (Singapore)", "zone": "territorial"},
]
LOC_MAP = {l["id"]: l for l in LOCATIONS}

MISSIONS = [
    {
        "id": 1,
        "title": "Introduction to Sovereignty",
        "brief": "Familiarize yourself with Indonesia's maritime zones. Plan a basic maritime security patrol in archipelagic waters.",
        "obj": "Conduct Maritime Security in Archipelagic Waters.",
        "req": {"ex": "marsec", "min_countries": 1, "loc_zone": "archipelagic"},
        "suggested_ex": "marsec",
        "suggested_loc": "java_sea",
        "suggested_countries": ["ID"],
        "category": "National",
        "events_pool": ["civilian_vessel"],
        "quiz_set": 0,
        "learn": [
            "Indonesia is an Archipelagic State under UNCLOS Part IV.",
            "Archipelagic Waters carry full sovereignty but must respect ALKI.",
            "Sovereignty ≠ Sovereign Rights."
        ]
    },
    {
        "id": 2,
        "title": "SAR Exercise — Indonesia & Australia",
        "brief": "Bilateral SAR exercise with Australia in the Arafura Sea. Focus on coordination and rescue procedures.",
        "obj": "Execute joint SAR with Australia.",
        "req": {"ex": "sar", "min_countries": 2, "loc_zone": "eez"},
        "suggested_ex": "sar",
        "suggested_loc": "arafura",
        "suggested_countries": ["ID", "AU"],
        "category": "Bilateral",
        "events_pool": ["weather_emergency"],
        "quiz_set": 1,
        "learn": [
            "Bilateral exercises build interoperability.",
            "Naval forces perform combat and a wide range of non-combat missions including SAR, HADR, maritime security and peace-support activities.",
            "Arafura Sea is within Indonesia's EEZ — freedom of navigation applies."
        ]
    },
    {
        "id": 3,
        "title": "ASEAN HADR — Solidarity Exercise",
        "brief": "Earthquake/tsunami struck. ASEAN activates HADR under ADMM-Plus. Coordinate multilateral humanitarian response.",
        "obj": "Lead ASEAN multilateral HADR.",
        "req": {"ex": "hadr", "min_countries": 3, "loc_zone": "archipelagic"},
        "suggested_ex": "hadr",
        "suggested_loc": "makassar",
        "suggested_countries": ["ID", "SG", "MY", "PH"],
        "category": "ASEAN",
        "events_pool": ["weather_emergency", "civilian_vessel"],
        "quiz_set": 2,
        "learn": [
            "ASEAN is NOT a military alliance like NATO.",
            "ADMM-Plus includes 8 dialogue partners.",
            "HADR builds highest regional trust with lowest tension."
        ]
    },
    {
        "id": 4,
        "title": "Maritime Security Patrol",
        "brief": "Illegal fishing/smuggling in North Natuna Sea. Plan patrol. Indonesia's maritime rights are addressed under its stated position and the UNCLOS framework. The simulation does not model every overlapping claim or maritime delimitation issue.",
        "obj": "Maritime security in North Natuna Sea.",
        "req": {"ex": "marsec", "min_countries": 1, "loc_zone": "eez"},
        "suggested_ex": "marsec",
        "suggested_loc": "natuna",
        "suggested_countries": ["ID"],
        "category": "National",
        "events_pool": ["foreign_warship", "neighbor_protest"],
        "quiz_set": 3,
        "learn": [
            "North Natuna Sea is Indonesia's EEZ, but overlapping claims exist.",
            "Indonesia's maritime rights are addressed under its stated position and the UNCLOS framework. The simulation does not model every overlapping claim or maritime delimitation issue.",
            "In EEZ, Indonesia has sovereign rights over resources, not full sovereignty."
        ]
    },
    {
        "id": 5,
        "title": "Combat Readiness — Super Garuda Shield",
        "brief": "Major multilateral combat readiness exercise. Legality depends on location, activity, applicable law, and safety/notification requirements.",
        "obj": "Multilateral combat readiness exercise.",
        "req": {"ex": "combat", "min_countries": 3, "loc_zone": "archipelagic"},
        "suggested_ex": "combat",
        "suggested_loc": "java_sea",
        "suggested_countries": ["ID", "US", "AU", "JP", "SG"],
        "category": "Multilateral",
        "events_pool": ["foreign_warship", "neighbor_protest", "civilian_vessel"],
        "quiz_set": 4,
        "learn": [
            "Super Garuda Shield is a major Indo-Pacific exercise.",
            "Combat exercises require strict adherence to safety and notification protocols.",
            "Multilateral exercises serve as Confidence-Building Measures (CBMs)."
        ]
    },
    {
        "id": 6,
        "title": "ZEE Incident — Foreign Military Activity",
        "brief": "Foreign warship conducting exercises in Indonesia's EEZ without notification. Legally disputed area.",
        "obj": "Manage foreign military activity in EEZ.",
        "req": {"ex": "marsec", "min_countries": 1, "loc_zone": "eez"},
        "suggested_ex": "marsec",
        "suggested_loc": "natuna",
        "suggested_countries": ["ID"],
        "category": "National",
        "events_pool": ["foreign_warship_eez"],
        "quiz_set": 5,
        "learn": [
            "Foreign military exercises in EEZ are DISPUTED under UNCLOS.",
            "Maritime powers say yes (Art 58). Coastal states say no (Art 56).",
            "Indonesia respects freedom of navigation but opposes activities disrupting resource exploitation."
        ]
    },
    {
        "id": 7,
        "title": "Navigation Crisis — Live Fire Safety",
        "brief": "Live fire exercise in Java Sea. Civilian vessel enters exclusion zone. Manage safety and issue warnings.",
        "obj": "Safely manage live fire with navigation incident.",
        "req": {"ex": "livefire", "min_countries": 1, "loc_zone": "archipelagic"},
        "suggested_ex": "livefire",
        "suggested_loc": "java_sea",
        "suggested_countries": ["ID"],
        "category": "National",
        "events_pool": ["civilian_vessel_live"],
        "quiz_set": 6,
        "learn": [
            "NOTAM/NAVTEX are SAFETY INFORMATION, not legal permissions.",
            "Certain activities listed in UNCLOS Article 19 may affect whether passage is considered innocent.",
            "Safety of civilian navigation is a paramount legal obligation."
        ]
    },
    {
        "id": 8,
        "title": "Regional Crisis — HADR + Diplomacy",
        "brief": "Major cyclone while diplomatic tensions are high. Launch HADR through contested waters.",
        "obj": "Execute HADR while managing diplomatic crisis.",
        "req": {"ex": "hadr", "min_countries": 3, "loc_zone": "eez"},
        "suggested_ex": "hadr",
        "suggested_loc": "pacific",
        "suggested_countries": ["ID", "AU", "PH", "JP"],
        "category": "ADMM-Plus",
        "events_pool": ["weather_emergency", "neighbor_protest", "foreign_warship"],
        "quiz_set": 7,
        "learn": [
            "HADR can proceed during diplomatic tensions.",
            "ADMM-Plus provides framework for practical security cooperation.",
            "UUD 1945 mandates Indonesia to participate in world order."
        ]
    },
]

# ═══════════════════════════════════════════════════════════
# SECTION 5 — DATA: EVENTS
# ═══════════════════════════════════════════════════════════
EVENTS = {
    "foreign_warship": {
        "title": "FOREIGN WARSHIP DETECTED",
        "desc": "A foreign warship is detected near the exercise area observing operations.",
        "legal_basis": "LEGAL CONTEXT — Apply the relevant UNCLOS maritime-zone regime and circumstances.",
        "choices": [
            {"text": "[A] Monitor and shadow", "stats": {"readiness": 2, "tension": 3, "safety": 0, "trust": 0, "legal": 0}, "complexity": "Low", "result": "Monitoring action recorded."},
            {"text": "[B] Establish radio comms", "stats": {"readiness": 0, "tension": -2, "safety": 2, "trust": 3, "legal": 0}, "complexity": "Low", "result": "Opened professional channel."},
            {"text": "[C] Diplomatic notification", "stats": {"readiness": 0, "tension": 1, "safety": 0, "trust": 2, "legal": 0}, "complexity": "Medium", "result": "Formal diplomatic exchange initiated."},
            {"text": "[D] Aggressive interception", "stats": {"readiness": 0, "tension": 20, "safety": -10, "trust": -10, "legal": -5}, "complexity": "High", "result": "Severe escalation penalties applied."}
        ]
    },
    "foreign_warship_eez": {
        "title": "FOREIGN MILITARY EXERCISE IN YOUR EEZ",
        "desc": "Foreign warship conducting weapons exercises in Indonesia's EEZ without notification. LEGAL INTERPRETATION DISPUTED.",
        "legal_basis": "DISPUTED INTERPRETATION — UNCLOS Art. 56 vs Art. 58. Due Regard applies.",
        "choices": [
            {"text": "[A] Monitor and document", "stats": {"readiness": 2, "tension": 2, "safety": 0, "trust": 0, "legal": 0}, "complexity": "Medium", "result": "Non-escalatory response."},
            {"text": "[B] Shadow with patrol", "stats": {"readiness": 3, "tension": 5, "safety": -2, "trust": 0, "legal": 0}, "complexity": "Medium", "result": "Shadowing conducted."},
            {"text": "[C] Diplomatic protest", "stats": {"readiness": 0, "tension": 5, "safety": 0, "trust": -2, "legal": 2}, "complexity": "High", "result": "Protest filed."},
            {"text": "[D] Force them out", "stats": {"readiness": 0, "tension": 25, "safety": -15, "trust": -15, "legal": -10}, "complexity": "Critical", "result": "Severe escalation."}
        ]
    },
    "civilian_vessel": {
        "title": "CIVILIAN VESSEL IN EXERCISE AREA",
        "desc": "Civilian fishing vessel entered exercise area. May be unaware of military operations.",
        "legal_basis": "LEGAL CONTEXT — Apply the relevant UNCLOS maritime-zone regime and circumstances.",
        "choices": [
            {"text": "[A] Issue radio warning", "stats": {"readiness": 0, "tension": 0, "safety": 5, "trust": 2, "legal": 2}, "complexity": "Low", "result": "Safety maintained."},
            {"text": "[B] Suspend temporarily", "stats": {"readiness": -3, "tension": 0, "safety": 8, "trust": 3, "legal": 3}, "complexity": "Low", "result": "Safety maximized."},
            {"text": "[C] Ignore vessel", "stats": {"readiness": 2, "tension": 5, "safety": -15, "trust": -5, "legal": -5}, "complexity": "High", "result": "Severe safety penalties."}
        ]
    },
    "civilian_vessel_live": {
        "title": "CIVILIAN VESSEL IN LIVE FIRE ZONE",
        "desc": "URGENT: Civilian vessel in live fire exclusion zone. Live ammunition in use.",
        "legal_basis": "MARITIME SAFETY FRAMEWORK — SOLAS. NOTAM/NAVTEX are safety info, not universal authorization.",
        "choices": [
            {"text": "[A] CEASE FIRE", "stats": {"readiness": -5, "tension": 0, "safety": 10, "trust": 5, "legal": 5}, "complexity": "Low", "result": "Safety prioritized."},
            {"text": "[B] Warning shots", "stats": {"readiness": 0, "tension": 8, "safety": -5, "trust": -3, "legal": -3}, "complexity": "Medium", "result": "Moderate penalties."},
            {"text": "[C] Continue firing", "stats": {"readiness": 3, "tension": 15, "safety": -25, "trust": -10, "legal": -10}, "complexity": "Critical", "result": "Severe penalties."}
        ]
    },
    "neighbor_protest": {
        "title": "NEIGHBORING COUNTRY PROTESTS",
        "desc": "Neighboring country issued diplomatic protest claiming exercise destabilizes region.",
        "legal_basis": "STATE POSITION / ASEAN Framework.",
        "choices": [
            {"text": "[A] Diplomatic clarification", "stats": {"readiness": 0, "tension": -3, "safety": 0, "trust": 3, "legal": 2}, "complexity": "Low", "result": "Tension decreases."},
            {"text": "[B] Modify exercise scope", "stats": {"readiness": -5, "tension": -5, "safety": 3, "trust": 5, "legal": 0}, "complexity": "Medium", "result": "Relations improve."},
            {"text": "[C] Ignore protest", "stats": {"readiness": 3, "tension": 10, "safety": 0, "trust": -8, "legal": 0}, "complexity": "Medium", "result": "Tension increases."},
            {"text": "[D] Suspend exercise", "stats": {"readiness": -10, "tension": -8, "safety": 5, "trust": 8, "legal": 0}, "complexity": "Low", "result": "Goodwill gained."}
        ]
    },
    "weather_emergency": {
        "title": "SEVERE WEATHER EMERGENCY",
        "desc": "Severe storm approaching. Sea state deteriorating rapidly.",
        "legal_basis": "LEGAL CONTEXT — Master's prerogative for safety of life at sea (SOLAS).",
        "choices": [
            {"text": "[A] Suspend, seek safe harbor", "stats": {"readiness": -5, "tension": 0, "safety": 10, "trust": 3, "legal": 0}, "complexity": "Low", "result": "Personnel safe."},
            {"text": "[B] Continue reduced scope", "stats": {"readiness": 2, "tension": 0, "safety": -5, "trust": 0, "legal": 0}, "complexity": "Medium", "result": "Some risk."},
            {"text": "[C] Full speed ahead", "stats": {"readiness": 5, "tension": 0, "safety": -15, "trust": -3, "legal": -2}, "complexity": "High", "result": "Severe safety penalties."}
        ]
    },
}

# ═══════════════════════════════════════════════════════════
# SECTION 6 — DATA: QUIZ & ENCYCLOPEDIA
# ═══════════════════════════════════════════════════════════
QUIZ_BANK = [
    [
        {"q": "Is the EEZ sovereign territory of Indonesia?", "opts": ["Yes", "No"], "ans": 1, "exp": "No. Indonesia has sovereign RIGHTS over resources, but NOT sovereignty. EEZ is not territory."},
        {"q": "What is an Archipelagic State?", "opts": ["State with islands", "State constituted wholly by archipelagos", "Any coastal state"], "ans": 1, "exp": "UNCLOS Part IV. Indonesia pioneered this via Djuanda Declaration 1957."},
        {"q": "Can foreign warships pass through territorial sea?", "opts": ["Never", "Yes, innocent passage", "Only with permission"], "ans": 1, "exp": "Yes, Innocent Passage (Art 17-19). Must not conduct weapons exercises."}
    ],
    [
        {"q": "What does SAR stand for?", "opts": ["Strategic Area Response", "Search and Rescue", "Sovereign Airspace"], "ans": 1, "exp": "Search and Rescue. Critical non-combat naval mission."},
        {"q": "Is bilateral exercise between two countries?", "opts": ["Yes", "No", "Only ASEAN"], "ans": 0, "exp": "Yes. Three or more is multilateral."}
    ],
    [
        {"q": "Is ASEAN a military alliance like NATO?", "opts": ["Yes", "No"], "ans": 1, "exp": "No. ASEAN is based on non-intervention and peaceful dispute resolution."},
        {"q": "What does ADMM-Plus include?", "opts": ["Only ASEAN", "ASEAN + 8 dialogue partners", "All UN"], "ans": 1, "exp": "10 ASEAN + 8 partners (US, China, Japan, etc.)."}
    ],
    [
        {"q": "Does Indonesia recognize China's Nine-Dash Line?", "opts": ["Yes", "No"], "ans": 1, "exp": "No. Rejected as having no legal basis under UNCLOS."},
        {"q": "In EEZ, can foreign ships navigate freely?", "opts": ["No", "Yes, freedom of navigation", "Only civilian"], "ans": 1, "exp": "Yes, Art. 58. But must have 'due regard' for coastal state rights."}
    ],
    [
        {"q": "Does the UN Charter itself require UN authorization for every military exercise?", "opts": ["Yes", "No", "Only in EEZ"], "ans": 1, "exp": "The UN Charter regulates, among other things, the threat or use of force. Whether a particular military exercise is lawful can also depend on the location, activity, applicable international rules, national law, safety requirements, and other circumstances."}
    ],
    [
        {"q": "Is foreign military exercise in another's EEZ legal?", "opts": ["Yes, always", "No, never", "Legally disputed"], "ans": 2, "exp": "DISPUTED. Maritime powers say yes. Coastal states say no. UNCLOS doesn't explicitly resolve."},
        {"q": "Can a coastal state use force to stop a foreign military exercise in its EEZ?", "opts": ["Yes, always", "No, never", "It involves complex legal and escalation considerations"], "ans": 2, "exp": "Military activity in an EEZ can involve overlapping legal considerations. The simulation does not determine every real-world dispute; it models escalation, safety, and selected legal-rule effects."}
    ],
    [
        {"q": "What is NOTAM/NAVTEX?", "opts": ["Legal permissions", "Safety information", "Tactical manuals"], "ans": 1, "exp": "Safety information to warn civilian traffic. Not legal authorization for the exercise."}
    ],
    [
        {"q": "What mandates Indonesia's participation in world order?", "opts": ["Article 1", "Preamble UUD 1945", "Article 33"], "ans": 1, "exp": "Preamble UUD 1945."},
        {"q": "Indonesia's peacekeeping contingent?", "opts": ["Garuda", "Eagle", "Nusantara"], "ans": 0, "exp": "Kontingen Garuda."}
    ],
]

ENCYCLOPEDIA = [
    {"title": "Internal Waters", "text": "Landward of baseline. Full sovereignty. Passage is generally subject to the coastal State's jurisdiction, subject to applicable UNCLOS exceptions. [LEGAL RULE — UNCLOS Art. 8]"},
    {"title": "Archipelagic Waters", "text": "Enclosed by archipelagic baselines. Full sovereignty but must allow Innocent Passage and ALKI. [LEGAL RULE — UNCLOS Part IV]"},
    {"title": "Territorial Sea", "text": "Up to 12 NM. Full sovereignty. Foreign ships may exercise innocent passage when the passage meets the applicable legal conditions. [LEGAL RULE — UNCLOS Art. 2-3, 17-19]"},
    {"title": "Contiguous Zone", "text": "Up to 24 NM. Not sovereign territory. Limited jurisdiction for customs, fiscal, immigration, sanitary. [LEGAL RULE — UNCLOS Art. 33]"},
    {"title": "Exclusive Economic Zone (EEZ)", "text": "Up to 200 NM. SOVEREIGN RIGHTS (not sovereignty) over resources. Freedom of navigation applies. Military activities involve differing State practices and legal interpretations; this simulation does not resolve every such dispute."},
    {"title": "Continental Shelf", "text": "Seabed/subsoil to 200-350 NM. Sovereign rights over seabed resources. Does not affect water column. [LEGAL RULE — UNCLOS Art. 76-77]"},
    {"title": "High Seas vs The Area", "text": "High Seas: Water column beyond EEZ. Res Communis (Freedom of the High Seas). The Area: Seabed beyond national jurisdiction. Common Heritage of Mankind. [LEGAL RULE — UNCLOS Part VII & XI]"},
    {"title": "Innocent Passage", "text": "Right to pass through territorial sea continuously/expeditiously. Certain activities listed in UNCLOS Article 19 may affect whether passage is considered innocent, depending on the circumstances. UNCLOS does not universally require prior permission for warships, though some states practice it."},
    {"title": "NOTAM & NAVTEX", "text": "NOTAM (aviation) and NAVTEX (maritime) are information/warning mechanisms for safety. They do not constitute legal permissions or authorizations for military exercises, nor do they replace other applicable legal/administrative requirements."},
    {"title": "Sovereignty vs Sovereign Rights", "text": "Sovereignty = full territorial control. Sovereign Rights = specific economic rights over resources without territorial ownership (e.g., in EEZ)."},
    {"title": "Due Regard", "text": "Principle requiring states to respect each other's rights in the EEZ. Central to the dispute over military activities."},
    {"title": "UN Charter Art. 2(4) & 51", "text": "Art. 2(4): Prohibits threat/use of force. Art. 51: Inherent right of self-defense. Neither prohibits military exercises."},
    {"title": "ASEAN & ADMM-Plus", "text": "ASEAN: Non-intervention, peaceful resolution. NOT a military alliance. ADMM-Plus: 10 ASEAN + 8 partners for practical security (HADR, maritime security)."},
    {"title": "Maritime Claims (e.g., Natuna)", "text": "Indonesia maintains maritime rights under UNCLOS and has stated positions concerning overlapping maritime claims. This simulation does not model every maritime delimitation or competing claim."},
]

# ═══════════════════════════════════════════════════════════
# SECTION 7 — MAP GEOMETRY & HELPERS
# ═══════════════════════════════════════════════════════════
MAP_X, MAP_Y, MAP_W, MAP_H = 20, 70, 780, 480

ISLANDS = {
    "Sumatra": [(30,80),(60,55),(100,70),(150,120),(200,175),(235,220),(255,265),(245,285),(225,265),(185,215),(135,160),(85,110),(40,90)],
    "Java": [(210,310),(260,295),(320,290),(380,295),(430,305),(445,318),(435,328),(385,322),(325,318),(265,318),(215,322)],
    "Kalimantan": [(285,80),(345,55),(410,65),(450,100),(460,155),(450,205),(420,245),(375,265),(335,255),(305,225),(285,185),(275,130)],
    "Sulawesi": [(485,120),(515,95),(540,115),(530,155),(545,180),(565,205),(555,235),(535,255),(515,235),(505,205),(495,175),(485,150)],
    "Papua": [(625,150),(685,125),(745,135),(765,170),(755,215),(725,245),(685,255),(645,235),(625,200)],
    "Bali": [(452,312),(462,307),(468,318),(458,323)],
    "Lombok": [(478,312),(488,307),(493,318),(483,323)],
}

NEIGHBORS = [
    {"name": "Malaysia", "pts": [(15,10),(65,8),(85,45),(55,68),(25,50)], "lx": 35, "ly": 25},
    {"name": "Singapore", "pts": [(105,60),(115,58),(118,65),(108,67)], "lx": 85, "ly": 55},
    {"name": "Philippines", "pts": [(555,5),(610,5),(625,45),(600,75),(565,55)], "lx": 565, "ly": 20},
    {"name": "PNG", "pts": [(765,145),(780,135),(780,225),(765,235)], "lx": 762, "ly": 170},
    {"name": "Australia", "pts": [(80,430),(720,430),(720,478),(80,478)], "lx": 370, "ly": 450},
]

SEA_LABELS = [
    ("Java Sea", 330, 355),
    ("South China Sea", 220, 100),
    ("North Natuna Sea", 310, 130),
    ("Makassar Str.", 465, 290),
    ("Arafura Sea", 680, 390),
    ("Indian Ocean", 200, 450),
    ("Pacific", 730, 80),
]

ZONE_REGIONS = [
    {"id": "internal", "rect": (200, 290, 260, 50)},
    {"id": "archipelagic", "rect": (100, 200, 500, 150)},
    {"id": "territorial", "rect": (80, 180, 540, 190)},
    {"id": "contiguous", "rect": (60, 160, 580, 230)},
    {"id": "eez", "rect": (30, 80, 750, 380)},
    {"id": "high", "rect": (0, 0, 780, 480)},
]


def get_zone_legal_context(zone):
    if zone == "eez":
        return "Applicable UNCLOS framework depends on the activity and circumstances; EEZ rights and duties are distinct from territorial sovereignty."
    elif zone == "territorial":
        return "Applicable framework includes the territorial-sea regime and the rules governing passage, subject to the specific circumstances."
    elif zone == "archipelagic":
        return "Applicable framework depends on the archipelagic-water and passage regime and the circumstances."
    elif zone == "high":
        return "Applicable framework includes the high-seas regime and relevant international obligations."
    elif zone == "internal":
        return "Applicable framework depends on the status of the waters and applicable passage rules."
    else:
        return "Applicable legal framework depends on the maritime zone and activity."


# ═══════════════════════════════════════════════════════════
# SECTION 8 — UTILITY & UI CLASSES
# ═══════════════════════════════════════════════════════════
def get_font(size):
    if os.environ.get("SDL_VIDEODRIVER") == "dummy":
        return pygame.font.Font(None, size)

    for name in ["consolas", "monospace", "couriernew"]:
        try:
            f = pygame.font.SysFont(name, size)
            if f:
                return f
        except Exception:
            pass
    return pygame.font.Font(None, size)


FONT_SM = FONT_MD = FONT_LG = FONT_XL = FONT_TTL = None


def init_fonts():
    global FONT_SM, FONT_MD, FONT_LG, FONT_XL, FONT_TTL
    FONT_SM, FONT_MD, FONT_LG, FONT_XL, FONT_TTL = get_font(14), get_font(18), get_font(22), get_font(28), get_font(38)


def draw_text(surf, text, x, y, font=None, color=C_TEXT):
    if not font:
        font = FONT_MD
    surf.blit(font.render(text, True, color), (x, y))


def draw_text_center(surf, text, cx, y, font=None, color=C_TEXT):
    if not font:
        font = FONT_MD
    s = font.render(text, True, color)
    surf.blit(s, (cx - s.get_width() // 2, y))


def draw_text_wrap(surf, text, x, y, max_w, font=None, color=C_TEXT, line_h=18):
    if not font:
        font = FONT_SM
    words, lines, cur = text.split(' '), [], ""
    for w in words:
        test = cur + (" " if cur else "") + w
        if font.size(test)[0] <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    for i, line in enumerate(lines):
        surf.blit(font.render(line, True, color), (x, y + i * line_h))
    return len(lines) * line_h


def draw_panel(surf, x, y, w, h, bc=C_BORDER):
    pygame.draw.rect(surf, C_PANEL, (x, y, w, h))
    pygame.draw.rect(surf, bc, (x, y, w, h), 1)


def draw_bar(surf, x, y, w, h, val, mx=100, col=C_ACCENT):
    pygame.draw.rect(surf, (30, 30, 40), (x, y, w, h))
    pygame.draw.rect(surf, col, (x, y, int(w * max(0, min(val, mx)) / mx), h))
    pygame.draw.rect(surf, C_BORDER, (x, y, w, h), 1)


def draw_poly(surf, pts, col, ox=0, oy=0):
    if len(pts) >= 3:
        pygame.draw.polygon(surf, col, [(px + ox, py + oy) for px, py in pts])


class Button:
    def __init__(self, x, y, w, h, text, action=None, color=C_BTN):
        self.rect = pygame.Rect(x, y, w, h)
        self.text, self.action, self.color = text, action, color
        self.hovered, self.active, self.enabled = False, False, True

    def draw(self, surf):
        c = self.color if self.enabled else (30, 30, 35)
        if self.active:
            c = C_BTN_ACT
        elif self.hovered:
            c = C_BTN_HOV
        pygame.draw.rect(surf, c, self.rect)
        pygame.draw.rect(surf, C_BORDER, self.rect, 1)
        draw_text_center(surf, self.text, self.rect.centerx, self.rect.y + 6, FONT_SM, C_TEXT if self.enabled else C_DIM)

    def check(self, mx, my):
        self.hovered = self.rect.collidepoint(mx, my) and self.enabled

    def click(self, mx, my):
        if self.rect.collidepoint(mx, my) and self.enabled:
            play("click")
            return True
        return False


# ═══════════════════════════════════════════════════════════
# SECTION 9 — MAIN GAME CLASS
# ═══════════════════════════════════════════════════════════
class Game:
    def __init__(self, headless=False):
        self.headless = headless
        if not headless:
            pygame.init()
            self.screen = pygame.display.set_mode((W, H))
            pygame.display.set_caption("BLOON WAR GAMES v0.1.2f — Sovereignty & Diplomacy")
            self.clock = pygame.time.Clock()
            init_fonts()
            init_sounds()
        else:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            os.environ["SDL_AUDIODRIVER"] = "dummy"
            pygame.init()
            self.screen = pygame.Surface((W, H))
            self.clock = pygame.time.Clock()
            init_fonts()

        self.state = "MENU"
        self.prev_state = "MENU"
        self.running = True
        self.radar_angle = 0
        self.tick = 0

        # GLOBAL STATS
        self.readiness = 50
        self.diplomacy = 60
        self.safety = 70
        self.tension = 20
        self.trust = 55
        self.legal_score = 50

        # MISSION STATE
        self.current_mission_idx = 0
        self.mission = None
        self.selected_ex = None
        self.selected_loc = None
        self.selected_countries = ["ID"]
        self.exercise_progress = 0
        self.exercise_running = False
        self.current_event = None
        self.current_event_id = None
        self.event_result = ""
        self.mission_failed = False
        self.failure_reason = ""
        self.ledger = {}
        self.event_history = []
        self.event_cooldown = 0
        self.triggered_events_count = 0
        self.max_events_per_mission = 2
        self.comms_log = []
        self.mission_results = {}
        self.mission_start_stats = {}
        self.event_choice_rects = []

        # QUIZ & ENCYCLOPEDIA
        self.quiz_questions = []
        self.quiz_idx = 0
        self.quiz_score = 0
        self.quiz_answered = False
        self.quiz_selected = -1
        self.enc_idx = 0
        self.buttons = []

        # FIX: build initial MENU buttons on first startup
        self.build_buttons()

    # --- TESTABLE HELPERS ---
    def snapshot_stats(self):
        return {k: (self.legal_score if k == "legal" else getattr(self, k)) for k in STAT_KEYS}

    def make_empty_ledger(self):
        return {phase: {k: 0 for k in STAT_KEYS} for phase in ("base", "modifier", "event")}

    def get_available_events(self):
        pool = self.mission.get("events_pool", [])
        history_ids = {h["event_id"] for h in self.event_history}
        return [e for e in pool if e not in history_ids]

    def evaluate_objective(self):
        req = self.mission.get("req", {})
        if req.get("ex") and self.selected_ex != req["ex"]:
            return False
        if req.get("min_countries") and len(self.selected_countries) < req["min_countries"]:
            return False
        if req.get("loc_zone") and LOC_MAP[self.selected_loc]["zone"] != req["loc_zone"]:
            return False
        return True

    def get_planning_rects(self):
        ex_r = [pygame.Rect(PLAN_X, PLAN_EX_Y + i * PLAN_ROW_H, PLAN_BTN_W, PLAN_BTN_H) for i in range(len(EXERCISE_TYPES))]
        loc_r = [pygame.Rect(PLAN_X, PLAN_LOC_Y + i * PLAN_ROW_H, PLAN_BTN_W, PLAN_BTN_H) for i in range(len(LOCATIONS))]
        part_r = [pygame.Rect(PLAN_PART_X, PLAN_PART_Y + i * PLAN_ROW_H, PLAN_BTN_W, PLAN_BTN_H) for i in range(len(COUNTRIES))]
        return ex_r, loc_r, part_r

    def compute_event_layout(self):
        ev = self.current_event
        y = 100 + 40
        y += draw_text_wrap(self.screen, ev["desc"], 130, y, W - 280, FONT_MD, C_TEXT, 22) + 10
        y += 16 + draw_text_wrap(self.screen, ev["legal_basis"], 130, y, W - 280, FONT_SM, C_DIM, 16) + 10
        y += 28
        rects = []
        for ch in ev["choices"]:
            rects.append(pygame.Rect(130, y, W - 280, 36))
            y += 42
        self.event_choice_rects = rects

    def clamp_stats(self):
        self.readiness = max(0, min(100, self.readiness))
        self.diplomacy = max(0, min(100, self.diplomacy))
        self.safety = max(0, min(100, self.safety))
        self.tension = max(0, min(100, self.tension))
        self.trust = max(0, min(100, self.trust))
        self.legal_score = max(0, min(100, self.legal_score))

    def set_state(self, s):
        self.prev_state = self.state
        self.state = s
        self.buttons = []
        self.build_buttons()

    def build_buttons(self):
        self.buttons = []
        if self.state == "MENU":
            self.buttons.extend([
                Button(W//2 - 120, 340, 240, 40, "START CAMPAIGN", "start"),
                Button(W//2 - 120, 395, 240, 40, "ENCYCLOPEDIA", "encyclopedia"),
                Button(W//2 - 120, 505, 240, 40, "QUIT", "quit"),
            ])
        elif self.state == "BRIEFING":
            self.buttons.extend([
                Button(W//2 - 120, H - 60, 240, 40, "PROCEED TO PLANNING", "plan"),
                Button(20, H - 60, 140, 40, "ENCYCLOPEDIA", "encyclopedia"),
            ])
        elif self.state == "PLANNING":
            self.buttons.extend([
                Button(W - 200, H - 60, 180, 40, "EXECUTE EXERCISE", "execute"),
                Button(20, H - 60, 140, 40, "MAP / ZONES", "map"),
                Button(170, H - 60, 140, 40, "ENCYCLOPEDIA", "encyclopedia"),
            ])
        elif self.state in ("MAP", "ENCYCLOPEDIA"):
            self.buttons.append(Button(W - 160, H - 50, 140, 36, "BACK", "back"))
            if self.state == "ENCYCLOPEDIA":
                self.buttons.extend([
                    Button(20, H - 50, 80, 36, "< PREV", "enc_prev"),
                    Button(110, H - 50, 80, 36, "NEXT >", "enc_next"),
                ])
        elif self.state == "EXECUTION":
            self.buttons.append(Button(W - 200, H - 55, 180, 36, "ENCYCLOPEDIA", "encyclopedia"))
        elif self.state == "RESULT":
            self.buttons.append(Button(W//2 - 120, H - 60, 240, 40, "TAKE QUIZ", "quiz"))

    def draw_bg(self):
        self.screen.fill(C_BG)
        for gx in range(0, W, 40):
            pygame.draw.line(self.screen, C_GRID, (gx, 0), (gx, H))
        for gy in range(0, H, 40):
            pygame.draw.line(self.screen, C_GRID, (0, gy), (W, gy))

    def draw_topbar(self, title=""):
        draw_panel(self.screen, 0, 0, W, 50, C_BORDER)
        draw_text(self.screen, "BLOON WAR GAMES v0.1.2f", 15, 8, FONT_LG, C_ACCENT)
        draw_text(self.screen, "SOVEREIGNTY & DIPLOMACY", 15, 30, FONT_SM, C_DIM)
        if title:
            draw_text(self.screen, title, W//2 - FONT_MD.size(title)[0]//2, 15, FONT_MD, C_WARN)

    def draw_stats(self, y=H - 110):
        draw_panel(self.screen, 0, y, W, 55)
        labels = [
            ("READINESS", self.readiness, C_ACCENT),
            ("DIPLOMACY", self.diplomacy, (100, 180, 255)),
            ("LEGAL", self.legal_score, (200, 100, 255)),
            ("SAFETY", self.safety, C_GOOD),
            ("TENSION", self.tension, C_DANGER),
            ("TRUST", self.trust, C_WARN),
        ]
        bx = 15
        for lbl, val, col in labels:
            draw_text(self.screen, lbl, bx, y + 5, FONT_SM, C_DIM)
            draw_bar(self.screen, bx, y + 22, 120, 14, val, 100, col)
            draw_text(self.screen, str(val), bx + 125, y + 20, FONT_SM, col)
            bx += 210

    def draw_radar(self, cx, cy, r):
        self.radar_angle = (self.radar_angle + 2) % 360
        pygame.draw.circle(self.screen, (15, 35, 50), (cx, cy), r, 1)
        pygame.draw.circle(self.screen, (15, 35, 50), (cx, cy), r//2, 1)
        rad = math.radians(self.radar_angle)
        pygame.draw.line(
            self.screen,
            C_ACCENT,
            (cx, cy),
            (cx + int(r * math.cos(rad)), cy + int(r * math.sin(rad))),
            1
        )

    def draw_map(self, ox=MAP_X, oy=MAP_Y, show_zones=True, highlight_zone=None):
        draw_panel(self.screen, ox - 2, oy - 2, MAP_W + 4, MAP_H + 4)
        pygame.draw.rect(self.screen, C_OCEAN, (ox, oy, MAP_W, MAP_H))
        draw_text(self.screen, "MAP MODE: [CONCEPTUAL] - Boundaries are schematic, not authoritative.", ox, oy - 15, FONT_SM, C_WARN)

        if show_zones:
            for zr in reversed(ZONE_REGIONS):
                if zr["id"] == "high":
                    continue
                col = ZONE_COLORS.get(zr["id"], C_OCEAN)
                s = pygame.Surface((MAP_W, MAP_H), pygame.SRCALPHA)
                s.fill((*col, 80 if zr["id"] == highlight_zone else 40))
                self.screen.blit(s, (ox, oy), zr["rect"])

        for gx in range(0, MAP_W, 60):
            pygame.draw.line(self.screen, C_GRID, (ox + gx, oy), (ox + gx, oy + MAP_H))
        for gy in range(0, MAP_H, 60):
            pygame.draw.line(self.screen, C_GRID, (ox, oy + gy), (ox + MAP_W, oy + gy))

        for nb in NEIGHBORS:
            draw_poly(self.screen, nb["pts"], (45, 55, 45), ox, oy)
            draw_text(self.screen, nb["name"], ox + nb["lx"], oy + nb["ly"], FONT_SM, C_DIM)

        for name, pts in ISLANDS.items():
            draw_poly(self.screen, pts, C_LAND, ox, oy)
            pygame.draw.polygon(self.screen, C_LAND2, [(px + ox, py + oy) for px, py in pts], 1)

        for lbl, lx, ly in SEA_LABELS:
            draw_text(self.screen, lbl, ox + lx, oy + ly, FONT_SM, (40, 70, 100))

        self.draw_radar(ox + MAP_W - 50, oy + 50, 35)

    def get_zone_at(self, mx, my):
        lx, ly = mx - MAP_X, my - MAP_Y
        if not (0 <= lx < MAP_W and 0 <= ly < MAP_H):
            return None
        for zr in ZONE_REGIONS:
            rx, ry, rw, rh = zr["rect"]
            if rx <= lx < rx + rw and ry <= ly < ry + rh:
                return zr["id"]
        return "high"

    # --- EVENT ENGINE ---
    def maybe_trigger_event(self):
        if self.triggered_events_count >= self.max_events_per_mission:
            return
        available = self.get_available_events()
        if not available:
            return
        event_id = random.choice(available)
        if event_id in EVENTS:
            self.trigger_event(EVENTS[event_id], event_id)

    def trigger_event(self, event_data, event_id):
        self.current_event = dict(event_data)
        zone = LOC_MAP[self.selected_loc]["zone"] if self.selected_loc else "high"
        self.current_event["legal_basis"] = event_data["legal_basis"] + " | ZONE CONTEXT: " + get_zone_legal_context(zone)
        self.current_event_id = event_id
        self.event_result = ""
        self.exercise_running = False
        self.compute_event_layout()
        self.set_state("EVENT")

    def apply_event_choice(self, choice):
        for k in STAT_KEYS:
            v = choice["stats"].get(k, 0)
            self.ledger["event"][k] += v
            if k == "legal":
                self.legal_score += v
            elif hasattr(self, k):
                setattr(self, k, getattr(self, k) + v)
        self.clamp_stats()

        self.event_history.append({
            "event": self.current_event["title"],
            "event_id": self.current_event_id,
            "choice": choice["text"],
            "effects": {k: choice["stats"].get(k, 0) for k in STAT_KEYS},
            "complexity": choice["complexity"]
        })

        self.event_result = choice["result"]

        if self.safety <= 0:
            self.mission_failed = True
            self.failure_reason = "Safety threshold breached."
        elif self.tension >= 100:
            self.mission_failed = True
            self.failure_reason = "Diplomatic tension critical."

        self.triggered_events_count += 1
        play("alert" if choice["stats"].get("tension", 0) > 10 or choice["stats"].get("safety", 0) < -10 else "ping")

    def resume_execution(self):
        self.current_event = None
        self.event_result = ""
        self.event_cooldown = 60
        if not self.mission_failed:
            self.exercise_running = True
            self.set_state("EXECUTION")
        else:
            self.finish_mission()

    # --- RENDERERS ---
    def render_menu(self):
        self.draw_bg()

        # Header
        draw_panel(self.screen, 24, 18, W - 48, 78)
        draw_text(self.screen, "BLOON WAR GAMES", 46, 30, FONT_TTL, C_ACCENT)
        draw_text(self.screen, "SOVEREIGNTY & DIPLOMACY", 46, 74, FONT_MD, C_WARN)
        draw_text(self.screen, "v0.1.2f", W - 165, 32, FONT_MD, C_DIM)

        draw_text_center(
            self.screen,
            "MARITIME STRATEGY, SOVEREIGNTY & DIPLOMATIC CRISIS SIMULATOR",
            W // 2,
            108,
            FONT_LG,
            C_TEXT
        )
        draw_text_center(
            self.screen,
            "EDUCATIONAL / CONCEPTUAL SIMULATION — NOT AN OPERATIONAL MILITARY SYSTEM",
            W // 2,
            138,
            FONT_SM,
            C_DIM
        )

        # Left panel: SYSTEM STATUS
        draw_panel(self.screen, 30, 170, 380, 380)
        draw_text(self.screen, "SYSTEM STATUS", 50, 185, FONT_MD, C_ACCENT)
        pygame.draw.line(self.screen, C_BORDER, (50, 212), (390, 212), 1)

        sys_items = [
            ("MISSION ENGINE", "READY"),
            ("EVENT ENGINE", "READY"),
            ("ACCOUNTING ENGINE", "READY"),
            ("UI GEOMETRY", "READY"),
            ("INTEGRATION TEST", "16/16 PASS"),
        ]
        y = 228
        for label, val in sys_items:
            draw_text(self.screen, label, 50, y, FONT_SM, C_TEXT)
            draw_text(self.screen, val, 270, y, FONT_SM, C_GOOD)
            y += 26

        pygame.draw.line(self.screen, C_BORDER, (50, 372), (390, 372), 1)
        draw_text(self.screen, "ALL SYSTEMS NOMINAL", 50, 388, FONT_SM, C_ACCENT)
        draw_text(self.screen, "CORE LEDGER: ENABLED", 50, 414, FONT_SM, C_DIM)
        draw_text(self.screen, "AAR MODE: ACTUAL APPLIED DELTA", 50, 436, FONT_SM, C_DIM)
        draw_text(self.screen, "MAP MODE: CONCEPTUAL", 50, 458, FONT_SM, C_DIM)
        draw_text(self.screen, "LEGAL MODEL: SIMPLIFIED UNCLOS", 50, 480, FONT_SM, C_DIM)

        # Center panel: COMMAND AUTHORITY
        draw_panel(self.screen, 430, 170, 420, 380)
        draw_text(self.screen, "COMMAND AUTHORITY", 450, 185, FONT_MD, C_ACCENT)
        pygame.draw.line(self.screen, C_BORDER, (450, 212), (830, 212), 1)

        draw_text(self.screen, "AUTHORIZATION: STRATEGIC OPERATIONS OFFICER", 450, 226, FONT_SM, C_TEXT)
        draw_text(self.screen, "MODE: EXERCISE PLANNING / CRISIS RESPONSE", 450, 248, FONT_SM, C_TEXT)
        draw_text(self.screen, "ROE: SIMULATED — NO LIVE WEAPONS", 450, 270, FONT_SM, C_TEXT)
        draw_text(self.screen, "LEGAL FRAMEWORK: UNCLOS / UN CHARTER", 450, 292, FONT_SM, C_TEXT)
        draw_text(self.screen, "> SYSTEM: Maritime command interface initialized.", 450, 316, FONT_SM, C_ACCENT)
        draw_text(self.screen, "> BLOON: No diplomatic incident detected... yet.", 450, 334, FONT_SM, C_DIM)
        draw_text(self.screen, "CAMPAIGN: 8 MISSIONS AVAILABLE", 450, 460, FONT_SM, C_DIM)
        draw_text(self.screen, "DECISION MODE: NON-DESTRUCTIVE", 450, 482, FONT_SM, C_DIM)

        # Right panel: MARITIME SURVEILLANCE
        draw_panel(self.screen, 870, 170, 380, 380)
        draw_text(self.screen, "MARITIME SURVEILLANCE", 890, 185, FONT_MD, C_ACCENT)
        pygame.draw.line(self.screen, C_BORDER, (890, 212), (1230, 212), 1)

        self.draw_radar(1060, 320, 88)

        draw_text(self.screen, "RADAR: ONLINE", 890, 435, FONT_SM, C_GOOD)
        draw_text(self.screen, "CONTACTS: --", 890, 457, FONT_SM, C_TEXT)
        draw_text(self.screen, "STATUS: NOMINAL", 890, 479, FONT_SM, C_TEXT)

        draw_text(self.screen, "SWEEP: ACTIVE", 1100, 435, FONT_SM, C_DIM)
        draw_text(self.screen, "SENSOR: PASSIVE", 1100, 457, FONT_SM, C_DIM)
        draw_text(self.screen, "ZONE: CONCEPTUAL", 1100, 479, FONT_SM, C_DIM)

        # Bottom panel: INITIAL OPERATIONAL STATUS
        draw_panel(self.screen, 30, 558, 1220, 110)
        draw_text(self.screen, "INITIAL OPERATIONAL STATUS", 50, 568, FONT_MD, C_ACCENT)
        pygame.draw.line(self.screen, C_BORDER, (50, 592), (1230, 592), 1)

        def stat_col(x, y, label, value, color):
            draw_text(self.screen, label, x, y, FONT_SM, C_DIM)
            draw_bar(self.screen, x + 95, y + 2, 150, 12, value, 100, color)
            draw_text(self.screen, str(value), x + 255, y, FONT_SM, color)

        stat_col(50, 606, "READINESS", self.readiness, C_ACCENT)
        stat_col(460, 606, "DIPLOMACY", self.diplomacy, (100, 180, 255))
        stat_col(870, 606, "SAFETY", self.safety, C_GOOD)

        stat_col(50, 636, "TENSION", self.tension, C_DANGER)
        stat_col(460, 636, "TRUST", self.trust, C_WARN)
        stat_col(870, 636, "LEGAL", self.legal_score, (200, 100, 255))

        draw_text(self.screen, "> SYSTEM: Awaiting commander input...", 30, 686, FONT_SM, C_ACCENT)
        draw_text(self.screen, "BUILD v0.1.2f — INITIALIZATION FIX", W - 360, 686, FONT_SM, C_DIM)

        for b in self.buttons:
            b.draw(self.screen)

    def render_briefing(self):
        self.draw_bg()
        self.draw_topbar(f"MISSION {self.mission['id']}: {self.mission['title']}")
        draw_panel(self.screen, 20, 60, W - 40, H - 130)
        y = 75
        draw_text(self.screen, "MISSION BRIEFING", 40, y, FONT_LG, C_ACCENT)
        y += 30
        y += draw_text_wrap(self.screen, self.mission["brief"], 40, y, W - 100, FONT_MD, C_TEXT, 22) + 10
        draw_text(self.screen, "OBJECTIVE:", 40, y, FONT_MD, C_WARN)
        y += 22
        y += draw_text_wrap(self.screen, self.mission["obj"], 40, y, W - 100, FONT_MD, C_TEXT, 22) + 10
        draw_text(self.screen, f"Suggested: {EX_MAP[self.mission['suggested_ex']]['name']} @ {LOC_MAP[self.mission['suggested_loc']]['name']}", 40, y, FONT_SM, C_DIM)
        y += 18
        draw_text(self.screen, "WHAT YOU WILL LEARN:", 40, y, FONT_MD, C_GOOD)
        y += 22
        for pt in self.mission["learn"]:
            draw_text(self.screen, f"  • {pt}", 40, y, FONT_SM, C_TEXT)
            y += 18
        self.draw_stats()
        for b in self.buttons:
            b.draw(self.screen)

    def render_planning(self):
        self.draw_bg()
        self.draw_topbar("PLANNING")
        self.draw_map(show_zones=True)
        self.draw_stats()

        draw_panel(self.screen, 810, 60, 460, H - 130)
        ex_r, loc_r, part_r = self.get_planning_rects()

        draw_text(self.screen, "EXERCISE TYPE", PLAN_X, 70, FONT_MD, C_ACCENT)
        for i, ex in enumerate(EXERCISE_TYPES):
            sel = self.selected_ex == ex["id"]
            rect = ex_r[i]
            pygame.draw.rect(self.screen, C_BTN_ACT if sel else C_BTN, rect)
            pygame.draw.rect(self.screen, C_BORDER, rect, 1)
            draw_text(self.screen, ex["name"], rect.x + 5, rect.y + 1, FONT_SM, C_BG if sel else C_TEXT)

        draw_text(self.screen, "LOCATION", PLAN_X, 250, FONT_MD, C_ACCENT)
        for i, loc in enumerate(LOCATIONS):
            sel = self.selected_loc == loc["id"]
            rect = loc_r[i]
            pygame.draw.rect(self.screen, C_BTN_ACT if sel else C_BTN, rect)
            pygame.draw.rect(self.screen, C_BORDER, rect, 1)
            draw_text(self.screen, f"{loc['name']} [{ZONES[loc['zone']]['name'].split('(')[0].strip()}]", rect.x + 5, rect.y + 1, FONT_SM, C_BG if sel else C_TEXT)

        draw_text(self.screen, "PARTICIPANTS", PLAN_PART_X, 70, FONT_MD, C_ACCENT)
        for i, co in enumerate(COUNTRIES):
            sel = co["id"] in self.selected_countries
            rect = part_r[i]
            pygame.draw.rect(self.screen, C_BTN_ACT if sel else C_BTN, rect)
            pygame.draw.rect(self.screen, C_BORDER, rect, 1)
            draw_text(self.screen, co["name"], rect.x + 5, rect.y + 1, FONT_SM, C_BG if sel else C_TEXT)

        for b in self.buttons:
            b.draw(self.screen)

    def render_map_view(self):
        self.draw_bg()
        self.draw_topbar("MARITIME ZONES — UNCLOS 1982")
        mx, my = pygame.mouse.get_pos()
        hz = self.get_zone_at(mx, my)
        self.draw_map(show_zones=True, highlight_zone=hz)

        px, py, pw, ph = 810, 60, 460, H - 120
        draw_panel(self.screen, px, py, pw, ph)
        y = py + 10
        draw_text(self.screen, "ZONE INFORMATION", px + 10, y, FONT_LG, C_ACCENT)
        y += 28

        if hz and hz in ZONES:
            z = ZONES[hz]
            draw_text(self.screen, f"Name: {z['name']}", px + 10, y, FONT_MD, C_TEXT)
            y += 22
            draw_text(self.screen, f"Sovereignty: {z['sovereignty']}", px + 10, y, FONT_MD, C_DANGER if "No" in z["sovereignty"] else C_GOOD)
            y += 22
            y += draw_text_wrap(self.screen, f"Navigation: {z['navigation']}", px + 10, y, pw - 20, FONT_SM, C_TEXT, 16) + 5
            draw_text(self.screen, f"Complexity: {z['complexity']}", px + 10, y, FONT_MD, C_DANGER if "HIGH" in z["complexity"] else C_GOOD)
            y += 22
            y += 5
            y += draw_text_wrap(self.screen, z["desc"], px + 10, y, pw - 20, FONT_SM, C_DIM, 16) + 5
            draw_text(self.screen, z["legal"], px + 10, y, FONT_SM, C_WARN)

        for b in self.buttons:
            b.draw(self.screen)

    def render_execution(self):
        self.draw_bg()
        self.draw_topbar(f"EXECUTING — {self.mission['title']}")
        self.draw_map()

        for i in range(5):
            bx = MAP_X + 100 + int(300 * math.sin(self.tick * 0.03 + i * 1.2))
            by = MAP_Y + 150 + int(100 * math.cos(self.tick * 0.04 + i * 0.8))
            pygame.draw.circle(self.screen, C_ACCENT, (bx, by), 3)

        draw_panel(self.screen, 810, 60, 460, 200)
        draw_text(self.screen, "EXERCISE IN PROGRESS", 825, 75, FONT_LG, C_ACCENT)
        draw_bar(self.screen, 825, 105, 430, 20, self.exercise_progress, 300, C_GOOD)
        draw_text(self.screen, f"{int(self.exercise_progress / 3)}%", 1260, 107, FONT_SM, C_TEXT)

        phase = "DEPLOYMENT" if self.exercise_progress < 100 else ("OPERATIONS" if self.exercise_progress < 200 else "RECOVERY")
        draw_text(self.screen, f"PHASE: {phase}", 825, 135, FONT_SM, C_WARN)

        draw_text(self.screen, "COMMS LOG:", 825, 160, FONT_SM, C_ACCENT)
        for i, msg in enumerate(self.comms_log[-4:]):
            draw_text(self.screen, msg, 825, 180 + i * 16, FONT_SM, C_DIM)

        self.draw_stats()
        for b in self.buttons:
            b.draw(self.screen)

    def render_event(self):
        self.draw_bg()
        self.draw_topbar("INCIDENT")
        ev = self.current_event

        draw_panel(self.screen, 100, 80, W - 200, H - 160)
        y = 100
        draw_text_center(self.screen, ev["title"], W//2, y, FONT_XL, C_DANGER)
        y += 40
        y += draw_text_wrap(self.screen, ev["desc"], 130, y, W - 280, FONT_MD, C_TEXT, 22) + 10

        draw_text(self.screen, "LEGAL BASIS & CONTEXT:", 130, y, FONT_SM, C_WARN)
        y += 16
        y += draw_text_wrap(self.screen, ev["legal_basis"], 130, y, W - 280, FONT_SM, C_DIM, 16) + 10

        draw_text(self.screen, "RESPONSE:", 130, y, FONT_MD, C_ACCENT)
        y += 28

        if not self.event_result:
            for rect, ch in zip(self.event_choice_rects, ev["choices"]):
                mx, my = pygame.mouse.get_pos()
                pygame.draw.rect(self.screen, C_BTN_HOV if rect.collidepoint(mx, my) else C_BTN, rect)
                pygame.draw.rect(self.screen, C_BORDER, rect, 1)
                draw_text(self.screen, ch["text"], rect.x + 10, rect.y + 8, FONT_SM, C_TEXT)
        else:
            draw_text(self.screen, "OUTCOME:", 130, y, FONT_MD, C_ACCENT)
            y += 22
            y += draw_text_wrap(self.screen, self.event_result, 130, y, W - 280, FONT_SM, C_TEXT, 16) + 10
            draw_text_center(self.screen, "[ Click to continue ]", W//2, y + 10, FONT_SM, C_DIM)

        self.draw_stats()

    def render_result(self):
        self.draw_bg()
        self.draw_topbar("AFTER ACTION REPORT")
        draw_panel(self.screen, 100, 70, W - 200, H - 140)
        y = 90
        r = self.mission_results
        final_delta = r.get("final_delta", {})

        if r.get("failed"):
            draw_text_center(self.screen, "MISSION ABORTED", W//2, y, FONT_XL, C_DANGER)
            draw_text_center(self.screen, r.get("fail_reason", ""), W//2, y + 35, FONT_MD, C_WARN)
            y += 70
        else:
            status = "MISSION COMPLETE" if r.get("obj_met") else "OBJECTIVE NOT MET"
            col = C_GOOD if r.get("obj_met") else C_WARN
            draw_text_center(self.screen, status, W//2, y, FONT_XL, col)
            y += 45

        draw_text(self.screen, "ACTUAL APPLIED DELTA:", 130, y, FONT_MD, C_ACCENT)
        y += 20

        for k in STAT_KEYS:
            v = final_delta.get(k, 0)
            col = C_GOOD if v >= 0 else C_DANGER
            draw_text(self.screen, f"  {k.capitalize():<12} {v:+d}", 150, y, FONT_MD, col)
            y += 22

        y += 10
        draw_text(self.screen, "LEGAL & DIPLOMATIC COMPLIANCE:", 130, y, FONT_MD, C_WARN)
        y += 22
        y += draw_text_wrap(self.screen, r.get("legal_text", ""), 150, y, W - 320, FONT_SM, C_TEXT, 16) + 15

        draw_text(self.screen, "LESSONS LEARNED:", 130, y, FONT_MD, C_ACCENT)
        y += 22
        for pt in self.mission.get("learn", []):
            if y > H - 100:
                break
            draw_text(self.screen, f"  • {pt}", 150, y, FONT_SM, C_TEXT)
            y += 18

        for b in self.buttons:
            b.draw(self.screen)

    def render_quiz(self):
        self.draw_bg()
        self.draw_topbar("KNOWLEDGE CHECK")

        if self.quiz_idx >= len(self.quiz_questions):
            draw_panel(self.screen, 100, 100, W - 200, 400)
            draw_text_center(self.screen, f"QUIZ COMPLETE — Score: {self.quiz_score}/{len(self.quiz_questions)}", W//2, 200, FONT_XL, C_ACCENT)
            draw_text_center(self.screen, "[ Click to continue ]", W//2, 300, FONT_MD, C_DIM)
            return

        q = self.quiz_questions[self.quiz_idx]
        draw_panel(self.screen, 100, 80, W - 200, H - 160)
        y = 100
        draw_text(self.screen, f"Question {self.quiz_idx + 1}/{len(self.quiz_questions)}", 130, y, FONT_SM, C_DIM)
        y += 25
        y += draw_text_wrap(self.screen, q["q"], 130, y, W - 280, FONT_LG, C_TEXT, 26) + 20

        for i, opt in enumerate(q["opts"]):
            rect = pygame.Rect(130, y, W - 280, 40)
            if self.quiz_answered:
                c = (30, 100, 50) if i == q["ans"] else ((100, 30, 30) if i == self.quiz_selected else C_BTN)
            else:
                mx, my = pygame.mouse.get_pos()
                c = C_BTN_HOV if rect.collidepoint(mx, my) else C_BTN
            pygame.draw.rect(self.screen, c, rect)
            pygame.draw.rect(self.screen, C_BORDER, rect, 1)
            draw_text(self.screen, f"  {chr(65 + i)}. {opt}", 140, y + 10, FONT_MD, C_TEXT)
            y += 48

        if self.quiz_answered:
            y += 10
            draw_text(self.screen, "EXPLANATION:", 130, y, FONT_MD, C_ACCENT)
            y += 22
            draw_text_wrap(self.screen, q["exp"], 130, y, W - 280, FONT_SM, C_TEXT, 16)
            draw_text_center(self.screen, "[ Click to continue ]", W//2, H - 100, FONT_SM, C_DIM)

    def render_encyclopedia(self):
        self.draw_bg()
        self.draw_topbar("UNCLOS & MARITIME LAW ENCYCLOPEDIA")
        draw_panel(self.screen, 40, 60, W - 80, H - 120)
        y = 75

        if 0 <= self.enc_idx < len(ENCYCLOPEDIA):
            entry = ENCYCLOPEDIA[self.enc_idx]
            draw_text(self.screen, f"[{self.enc_idx + 1}/{len(ENCYCLOPEDIA)}] {entry['title']}", 60, y, FONT_LG, C_ACCENT)
            y += 30
            draw_text_wrap(self.screen, entry["text"], 60, y, W - 140, FONT_MD, C_TEXT, 22)

        for b in self.buttons:
            b.draw(self.screen)

    # --- INPUT & LOGIC ---
    def handle_click(self, mx, my):
        for b in self.buttons:
            if b.click(mx, my):
                self.do_action(b.action)
                return

        if self.state == "PLANNING":
            ex_r, loc_r, part_r = self.get_planning_rects()
            for i, ex in enumerate(EXERCISE_TYPES):
                if ex_r[i].collidepoint(mx, my):
                    self.selected_ex = ex["id"]
                    return
            for i, loc in enumerate(LOCATIONS):
                if loc_r[i].collidepoint(mx, my):
                    self.selected_loc = loc["id"]
                    return
            for i, co in enumerate(COUNTRIES):
                if part_r[i].collidepoint(mx, my):
                    if co["id"] != "ID":
                        if co["id"] in self.selected_countries:
                            self.selected_countries.remove(co["id"])
                        else:
                            self.selected_countries.append(co["id"])
                    return

        elif self.state == "EVENT":
            if not self.event_result:
                for rect, ch in zip(self.event_choice_rects, self.current_event["choices"]):
                    if rect.collidepoint(mx, my):
                        self.apply_event_choice(ch)
                        return
            else:
                self.resume_execution()

        elif self.state == "QUIZ":
            if self.quiz_idx >= len(self.quiz_questions):
                if self.current_mission_idx < len(MISSIONS) - 1:
                    self.current_mission_idx += 1
                    self.start_mission()
                else:
                    self.set_state("MENU")
                return

            if not self.quiz_answered:
                q = self.quiz_questions[self.quiz_idx]
                y = 100 + 25 + draw_text_wrap(self.screen, q["q"], 130, 125, W - 280, FONT_LG, C_TEXT, 26) + 20
                for i in range(len(q["opts"])):
                    rect = pygame.Rect(130, y, W - 280, 40)
                    if rect.collidepoint(mx, my):
                        self.quiz_selected = i
                        self.quiz_answered = True
                        if i == q["ans"]:
                            self.quiz_score += 1
                            play("success")
                        else:
                            play("warn")
                        return
                    y += 48
            else:
                self.quiz_idx += 1
                self.quiz_answered = False
                self.quiz_selected = -1

    def do_action(self, action):
        if action == "quit":
            self.running = False
        elif action == "start":
            self.current_mission_idx = 0
            self.readiness = 50
            self.diplomacy = 60
            self.safety = 70
            self.tension = 20
            self.trust = 55
            self.legal_score = 50
            self.start_mission()
        elif action == "plan":
            self.set_state("PLANNING")
            self.selected_ex = self.mission["suggested_ex"]
            self.selected_loc = self.mission["suggested_loc"]
            self.selected_countries = list(self.mission["suggested_countries"])
        elif action == "execute":
            if self.selected_ex and self.selected_loc:
                self.start_execution()
        elif action == "map":
            self.set_state("MAP")
        elif action == "encyclopedia":
            self.set_state("ENCYCLOPEDIA")
        elif action == "back":
            self.set_state(self.prev_state if self.prev_state != self.state else "PLANNING")
        elif action == "enc_prev":
            self.enc_idx = (self.enc_idx - 1) % len(ENCYCLOPEDIA)
        elif action == "enc_next":
            self.enc_idx = (self.enc_idx + 1) % len(ENCYCLOPEDIA)
        elif action == "quiz":
            self.start_quiz()

    def start_mission(self):
        self.mission = MISSIONS[self.current_mission_idx]
        self.selected_ex = None
        self.selected_loc = None
        self.selected_countries = ["ID"]
        self.exercise_progress = 0
        self.mission_failed = False
        self.failure_reason = ""
        self.ledger = self.make_empty_ledger()
        self.event_history = []
        self.current_event = None
        self.current_event_id = None
        self.event_result = ""
        self.event_cooldown = 0
        self.triggered_events_count = 0
        self.comms_log = []
        self.mission_results = {}
        self.mission_start_stats = self.snapshot_stats()
        self.set_state("BRIEFING")

    def start_execution(self):
        self.exercise_progress = 0
        self.exercise_running = True
        self.comms_log = []
        self.set_state("EXECUTION")

        ex = EX_MAP[self.selected_ex]
        for k in STAT_KEYS:
            if k == "legal":
                self.ledger["base"][k] -= ex.get("legal_risk", 0)
            else:
                self.ledger["base"][k] += ex.get(k, 0)

        loc_zone = LOC_MAP[self.selected_loc]["zone"]
        if loc_zone == "eez" and self.selected_ex in ("asw", "livefire", "combat"):
            self.ledger["modifier"]["tension"] += 5

        if len(self.selected_countries) >= 3:
            self.ledger["modifier"]["trust"] += 5
            self.ledger["modifier"]["readiness"] += 3

        for phase in ["base", "modifier"]:
            for k in STAT_KEYS:
                v = self.ledger[phase][k]
                if k == "legal":
                    self.legal_score += v
                elif hasattr(self, k):
                    setattr(self, k, getattr(self, k) + v)
        self.clamp_stats()

    def start_quiz(self):
        qset = self.mission.get("quiz_set", 0)
        self.quiz_questions = list(QUIZ_BANK[qset] if qset < len(QUIZ_BANK) else QUIZ_BANK[0])
        self.quiz_idx = 0
        self.quiz_score = 0
        self.quiz_answered = False
        self.quiz_selected = -1
        self.set_state("QUIZ")

    def finish_mission(self):
        obj_met = self.evaluate_objective()
        end_stats = self.snapshot_stats()
        actual_applied_delta = {k: end_stats[k] - self.mission_start_stats[k] for k in STAT_KEYS}

        self.mission_results = {
            "obj_met": obj_met,
            "failed": self.mission_failed,
            "fail_reason": self.failure_reason,
            "ledger": self.ledger,
            "final_delta": actual_applied_delta
        }

        if self.mission_failed:
            self.mission_results["legal_text"] = f"MISSION ABORTED. {self.failure_reason}"
        elif not obj_met:
            self.mission_results["legal_text"] = "Objective NOT MET. Exercise parameters did not align with mission requirements."
        else:
            self.mission_results["legal_text"] = "Objective MET. No simulated rule violation was triggered."

        self.set_state("RESULT")
        play("success" if not self.mission_failed and obj_met else "alert")

    def run(self):
        while self.running:
            self.tick += 1
            mx, my = pygame.mouse.get_pos()
            for b in self.buttons:
                b.check(mx, my)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_click(event.pos[0], event.pos[1])
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if self.state in ("ENCYCLOPEDIA", "MAP"):
                        self.set_state(self.prev_state if self.prev_state != self.state else "PLANNING")
                    elif self.state == "MENU":
                        self.running = False

            if self.state == "EXECUTION" and self.exercise_running:
                self.exercise_progress += 1.0
                if self.event_cooldown > 0:
                    self.event_cooldown -= 1.0

                if self.exercise_progress >= 300:
                    self.exercise_running = False
                    self.finish_mission()
                elif self.event_cooldown <= 0 and self.triggered_events_count < self.max_events_per_mission:
                    if 50 < self.exercise_progress < 250:
                        if random.random() < 0.02:
                            self.maybe_trigger_event()

            if not self.headless:
                if self.state == "MENU":
                    self.render_menu()
                elif self.state == "BRIEFING":
                    self.render_briefing()
                elif self.state == "PLANNING":
                    self.render_planning()
                elif self.state == "MAP":
                    self.render_map_view()
                elif self.state == "EXECUTION":
                    self.render_execution()
                elif self.state == "EVENT":
                    self.render_event()
                elif self.state == "RESULT":
                    self.render_result()
                elif self.state == "QUIZ":
                    self.render_quiz()
                elif self.state == "ENCYCLOPEDIA":
                    self.render_encyclopedia()

                pygame.display.flip()
                self.clock.tick(FPS)
            else:
                break

        if not self.headless:
            pygame.quit()
            sys.exit()


# ═══════════════════════════════════════════════════════════
# SECTION 10 — SELF-TEST
# ═══════════════════════════════════════════════════════════
def run_self_test():
    print("[BLOON SELF-TEST v0.1.2f]")
    passed = 0
    total = 16
    game = Game(headless=True)

    def reset_game():
        game.current_mission_idx = 0
        game.mission = MISSIONS[0]
        game.selected_ex = None
        game.selected_loc = None
        game.selected_countries = ["ID"]
        game.exercise_progress = 0
        game.mission_failed = False
        game.failure_reason = ""
        game.ledger = game.make_empty_ledger()
        game.event_history = []
        game.current_event = None
        game.current_event_id = None
        game.event_result = ""
        game.event_cooldown = 0
        game.triggered_events_count = 0
        game.max_events_per_mission = 2
        game.comms_log = []
        game.mission_results = {}
        game.event_choice_rects = []
        game.readiness = 50
        game.diplomacy = 60
        game.safety = 70
        game.tension = 20
        game.trust = 55
        game.legal_score = 50
        game.mission_start_stats = game.snapshot_stats()

    # 1. Real legal sign
    try:
        reset_game()
        game.selected_ex = "combat"
        game.selected_loc = "java_sea"
        before = game.legal_score
        game.start_execution()
        expected_risk = EX_MAP["combat"]["legal_risk"]
        if game.ledger["base"]["legal"] == -expected_risk and game.legal_score == before - expected_risk:
            print("[PASS] Real legal sign")
            passed += 1
        else:
            print("[FAIL] Real legal sign")
    except Exception as e:
        print(f"[FAIL] Real legal sign: {e}")

    # 2. Real base ledger
    try:
        reset_game()
        game.selected_ex = "marsec"
        game.selected_loc = "java_sea"
        before = game.snapshot_stats()
        game.start_execution()
        after = game.snapshot_stats()
        delta = {k: after[k] - before[k] for k in STAT_KEYS}
        expected = {k: game.ledger["base"][k] + game.ledger["modifier"][k] for k in STAT_KEYS}
        if delta == expected:
            print("[PASS] Real base ledger")
            passed += 1
        else:
            print("[FAIL] Real base ledger")
    except Exception as e:
        print(f"[FAIL] Real base ledger: {e}")

    # 3. Real EEZ modifier
    try:
        reset_game()
        game.selected_ex = "asw"
        game.selected_loc = "natuna"
        game.start_execution()
        if game.ledger["modifier"]["tension"] == 5:
            print("[PASS] Real EEZ modifier")
            passed += 1
        else:
            print("[FAIL] Real EEZ modifier")
    except Exception as e:
        print(f"[FAIL] Real EEZ modifier: {e}")

    # 4. Real participant modifier
    try:
        reset_game()
        game.selected_ex = "hadr"
        game.selected_loc = "makassar"
        game.selected_countries = ["ID", "AU", "SG"]
        game.start_execution()
        if game.ledger["modifier"]["trust"] == 5 and game.ledger["modifier"]["readiness"] == 3:
            print("[PASS] Real participant modifier")
            passed += 1
        else:
            print("[FAIL] Real participant modifier")
    except Exception as e:
        print(f"[FAIL] Real participant modifier: {e}")

    # 5. Real event application
    try:
        reset_game()
        game.selected_ex = "marsec"
        game.selected_loc = "java_sea"
        game.start_execution()
        before = game.snapshot_stats()
        game.current_event = EVENTS["civilian_vessel"]
        game.current_event_id = "civilian_vessel"
        game.apply_event_choice(EVENTS["civilian_vessel"]["choices"][0])
        after = game.snapshot_stats()
        delta = {k: after[k] - before[k] for k in STAT_KEYS}
        if delta == game.ledger["event"]:
            print("[PASS] Real event application")
            passed += 1
        else:
            print("[FAIL] Real event application")
    except Exception as e:
        print(f"[FAIL] Real event application: {e}")

    # 6. AAR actual applied delta
    try:
        reset_game()
        game.selected_ex = "combat"
        game.selected_loc = "natuna"
        game.selected_countries = ["ID", "AU", "SG"]
        game.start_execution()
        game.finish_mission()
        aar = game.mission_results
        ledger_sum = {
            k: aar["ledger"]["base"][k] + aar["ledger"]["modifier"][k] + aar["ledger"]["event"][k]
            for k in STAT_KEYS
        }
        if "final_delta" in aar and aar["final_delta"] == ledger_sum:
            print("[PASS] AAR actual applied delta")
            passed += 1
        else:
            print("[FAIL] AAR actual applied delta")
    except Exception as e:
        print(f"[FAIL] AAR actual applied delta: {e}")

    # 7. Global delta vs AAR
    try:
        reset_game()
        game.selected_ex = "marsec"
        game.selected_loc = "java_sea"
        before = game.snapshot_stats()
        game.start_execution()
        game.current_event = EVENTS["civilian_vessel"]
        game.current_event_id = "civilian_vessel"
        game.apply_event_choice(EVENTS["civilian_vessel"]["choices"][0])
        game.finish_mission()
        after = game.snapshot_stats()
        actual_global = {k: after[k] - before[k] for k in STAT_KEYS}
        if actual_global == game.mission_results["final_delta"]:
            print("[PASS] Global delta vs AAR")
            passed += 1
        else:
            print("[FAIL] Global delta vs AAR")
    except Exception as e:
        print(f"[FAIL] Global delta vs AAR: {e}")

    # 8. Clamp accounting
    try:
        reset_game()
        game.safety = 5
        game.mission_start_stats = game.snapshot_stats()
        game.selected_ex = "marsec"
        game.selected_loc = "java_sea"
        game.start_execution()
        game.current_event = EVENTS["civilian_vessel_live"]
        game.current_event_id = "civilian_vessel_live"
        game.apply_event_choice(EVENTS["civilian_vessel_live"]["choices"][2])
        game.finish_mission()

        if game.safety == 0 and game.ledger["event"]["safety"] == -25 and game.mission_results["final_delta"]["safety"] == -5:
            print("[PASS] Clamp accounting")
            passed += 1
        else:
            print("[FAIL] Clamp accounting")
    except Exception as e:
        print(f"[FAIL] Clamp accounting: {e}")

    # 9. Production event scheduler
    try:
        reset_game()
        game.mission = MISSIONS[0]
        game.selected_loc = "java_sea"
        original_choice = random.choice
        try:
            random.choice = lambda seq: seq[0]
            game.maybe_trigger_event()
        finally:
            random.choice = original_choice

        if game.state == "EVENT" and game.current_event_id == "civilian_vessel":
            print("[PASS] Production event scheduler")
            passed += 1
        else:
            print("[FAIL] Production event scheduler")
    except Exception as e:
        print(f"[FAIL] Production event scheduler: {e}")

    # 10. Event deduplication
    try:
        reset_game()
        game.mission = MISSIONS[4]
        game.event_history = [{"event_id": "foreign_warship"}]
        game.selected_loc = "java_sea"
        available = game.get_available_events()
        original_choice = random.choice
        try:
            random.choice = lambda seq: seq[0]
            game.maybe_trigger_event()
        finally:
            random.choice = original_choice

        if game.current_event_id in available and game.current_event_id != "foreign_warship":
            print("[PASS] Event deduplication")
            passed += 1
        else:
            print("[FAIL] Event deduplication")
    except Exception as e:
        print(f"[FAIL] Event deduplication: {e}")

    # 11. Event count limit
    try:
        reset_game()
        game.triggered_events_count = game.max_events_per_mission
        game.current_event_id = None
        original_choice = random.choice
        try:
            random.choice = lambda seq: seq[0]
            game.maybe_trigger_event()
        finally:
            random.choice = original_choice

        if game.current_event_id is None:
            print("[PASS] Event count limit")
            passed += 1
        else:
            print("[FAIL] Event count limit")
    except Exception as e:
        print(f"[FAIL] Event count limit: {e}")

    # 12. Event history integrity
    try:
        reset_game()
        game.current_event = EVENTS["civilian_vessel"]
        game.current_event_id = "civilian_vessel"
        game.apply_event_choice(EVENTS["civilian_vessel"]["choices"][0])
        h = game.event_history[0]
        if all(k in h for k in ["event_id", "event", "choice", "effects", "complexity"]):
            print("[PASS] Event history integrity")
            passed += 1
        else:
            print("[FAIL] Event history integrity")
    except Exception as e:
        print(f"[FAIL] Event history integrity: {e}")

    # 13. Production planning geometry
    try:
        ex_r, loc_r, part_r = game.get_planning_rects()
        all_r = ex_r + loc_r + part_r
        if (
            len(ex_r) == len(EXERCISE_TYPES)
            and len(loc_r) == len(LOCATIONS)
            and len(part_r) == len(COUNTRIES)
            and all(0 <= r.left and r.right <= W and 0 <= r.top and r.bottom <= H for r in all_r)
        ):
            print("[PASS] Production planning geometry")
            passed += 1
        else:
            print("[FAIL] Production planning geometry")
    except Exception as e:
        print(f"[FAIL] Production planning geometry: {e}")

    # 14. Production event geometry
    try:
        reset_game()
        game.current_event = EVENTS["civilian_vessel"]
        game.current_event_id = "civilian_vessel"
        game.compute_event_layout()
        rects = game.event_choice_rects
        if len(rects) == len(EVENTS["civilian_vessel"]["choices"]) and all(
            0 <= r.left and r.right <= W and 0 <= r.top and r.bottom <= H for r in rects
        ):
            print("[PASS] Production event geometry")
            passed += 1
        else:
            print("[FAIL] Production event geometry")
    except Exception as e:
        print(f"[FAIL] Production event geometry: {e}")

    # 15. Real objective evaluation
    try:
        reset_game()
        game.mission = MISSIONS[0]

        game.selected_ex = "marsec"
        game.selected_loc = "java_sea"
        game.selected_countries = ["ID"]
        if not game.evaluate_objective():
            raise Exception("Case A failed")

        game.selected_ex = "combat"
        if game.evaluate_objective():
            raise Exception("Case B failed")

        game.selected_ex = "marsec"
        game.selected_loc = "natuna"
        if game.evaluate_objective():
            raise Exception("Case C failed")

        game.selected_loc = "java_sea"
        game.selected_countries = []
        if game.evaluate_objective():
            raise Exception("Case D failed")

        print("[PASS] Real objective evaluation")
        passed += 1
    except Exception as e:
        print(f"[FAIL] Real objective evaluation: {e}")

    # 16. Production zone context
    try:
        reset_game()
        game.mission = MISSIONS[0]
        game.selected_loc = "natuna"
        game.event_history = []
        game.triggered_events_count = 0
        original_choice = random.choice
        try:
            random.choice = lambda seq: seq[0]
            game.maybe_trigger_event()
        finally:
            random.choice = original_choice

        if game.current_event and "ZONE CONTEXT" in game.current_event["legal_basis"]:
            print("[PASS] Production zone context")
            passed += 1
        else:
            print("[FAIL] Production zone context")
    except Exception as e:
        print(f"[FAIL] Production zone context: {e}")

    print(f"\nTOTAL: {passed}/{total} PASS")
    pygame.quit()
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        run_self_test()
    else:
        Game().run()