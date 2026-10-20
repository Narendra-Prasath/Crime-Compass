# BEHAVIORAL CONNECTION MAP: EMPIRICAL RELATIONSHIP NETWORK

## 1. Executive Summary & Design Philosophy

The **Behavioral Connection Map** provides an interactive, graph-based visualization of the relationships between **Crime Categories** and **Behavioral Patterns** discovered across 220,663 historical incidents.

In traditional crime analysis, offenses are rigidly divided into statutory legal categories (e.g., Larceny, Burglary, Robbery, Assault). The Behavioral Connection Map uncovers the underlying behavioral modus operandi links that bridge these categories, demonstrating how diverse legal classifications converge onto identical behavioral archetypes.

```text
Theft / Larceny
 ↘
  PATTERN 04 (Residential Infiltration)
 ↗
Burglary
```

### Critical Ethical & Investigative Constraint:
The graph represents **ONLY** behavioral similarity and pattern relationships.
The graph **MUST NOT** and **DOES NOT** represent:
- People
- Suspects
- Offenders
- Identities
- Criminal networks / Gang structures

---

## 2. Graph Topology & Ground Truth Architecture

The graph is modeled as a **bipartite / two-mode network** where relationships are computed directly from the unsupervised Spherical K-Means ($k=8$) cluster profiles and cross-crime discovery artifacts:

```text
CRIME CATEGORIES                                   BEHAVIORAL PATTERNS
(Statutory Offense Types)                          (Learned MO Archetypes)

[Property Crimes] ───────────────────────────────> [PATTERN 01: Small-City Property Theft]
(Theft, Burglary, Larceny)            │
                                      ├──────────> [PATTERN 02: Domestic/Person Assault]
[Violent Person Crimes] ──────────────┤
(Assault, Battery, Domestic)          ├──────────> [PATTERN 03: Suburban Daytime Theft]
                                      │
[Crimes Against Society] ─────────────┼──────────> [PATTERN 04: Residential Infiltration]
(Vice, Contraband, Public Order)      │
                                      ├──────────> [PATTERN 05: Weekend Nightlife Disorder]
[Confrontational Property] ───────────┤
(Robbery, Carjacking)                 ├──────────> [PATTERN 06: Commercial Enterprise Fraud]
                                      │
[Contraband & Vandalism] ─────────────┼──────────> [PATTERN 07: Metropolitan Core Shoplifting]
(Stolen Property, Destruction)        │
                                      └──────────> [PATTERN 08: Street Contraband & Weapons]
```

### Graph Components:
1. **Crime Category Nodes (7 nodes)**:
   - `Property Offenses`: Theft, Burglary, Larceny, Motor Vehicle Theft (111,244 historical cases, 50.4%)
   - `Violent Crimes Against Persons`: Assault, Domestic Violence, Battery (68,609 cases, 31.1%)
   - `Crimes Against Society`: Vice, Narcotics, Weapons, Public Order (33,400 cases, 15.1%)
   - `Confrontational Property Crimes`: Robbery, Carjacking, Home Invasion (5,304 cases, 2.4%)
   - `Contraband & Vandalism`: Stolen property trafficking, malicious mischief (1,313 cases, 0.6%)
   - `Public Disorder & Resisting`: Affray, obstruction, resisting enforcement (711 cases, 0.3%)
   - `Compound Multi-Domain Incidents`: Rioting, multi-crime escalation (77 cases, 0.03%)

2. **Behavioral Pattern Nodes (8 nodes)**:
   - Discovered archetypes `PATTERN 01` through `PATTERN 08` (`CCP_00` to `CCP_07`).

3. **Computed Edges (34 empirical connections)**:
   - Every edge represents an actual cross-category membership where historical incidents of that legal category were assigned to that behavioral archetype.
   - **Zero hardcoded edges**: Edge weights, incident volumes, and percentages are computed dynamically from `state.cross_crime_patterns`.

---

## 3. Interactive Connection Selection: Shared Behavioral DNA

When a user selects an edge (or clicks a connecting line in the interactive visualization), the system presents the **Shared Behavioral DNA** dossier explaining why that category and pattern are linked:

### Selected Connection Example:
`Property Crimes` $\leftrightarrow$ `PATTERN 04 (Residential Infiltration)`

```text
SHARED BEHAVIORAL DNA
Property Crimes ↔ PATTERN 04
Supporting Incidents: 33,065 historical cases (99.2% of pattern, 29.7% of category)
Cosine Convergence:   76.2% (Strong Behavioral Connection)

Shared Dimensions:
• TIME PATTERN:
  Nocturnal concentration (48.1% nighttime execution, 77.0% weekend)
• LOCATION & JURISDICTION:
  Residential dwellings and small municipal/suburban jurisdictions
• PROPERTY DYNAMICS:
  Targeted property acquisition (99.2% involved, mean loss: $3,240)
• WEAPON & METHOD:
  Unarmed execution (98.35% unarmed), covert structural entry tooling
• HARM & ENFORCEMENT:
  Physical injury: 1.57%, on-scene arrest rate: 9.38%

Matching Modus Operandi Traits:
✓ Nocturnal timing pattern
✓ Weekend concentration
✓ Property acquisition objective
✓ Unarmed execution
✓ Absence of bodily harm

Why Connected:
Incidents in 'Property' connect to 'PATTERN 04' because 33,065 historical cases
share identical operational DNA: nocturnal stealth entry without violent confrontation.
Statutory labels differ across jurisdictions, but the modus operandi is identical.
```

---

## 4. UI Layout & Architecture

To keep the primary incident analysis workflow clean and uncluttered, the Behavioral Connection Map is implemented as an **optional, dedicated interactive view**:

1. **Dedicated Page**: Accessible via navigation at `/connection-map` (`Connection Map`, badge `Graph`).
2. **Contextual Action Links**: Accessible directly from `Cross-Crime Links` and `Explore Patterns` via dedicated navigation buttons.
3. **Pure SVG / React Implementation**:
   - Zero bulky third-party graph dependencies (D3, Cytoscape, or vis.js avoided to prevent bundle bloat).
   - High-performance, responsive SVG cubic Bezier curve rendering (`M x1 y1 C cx1 y1, cx2 y2, x2 y2`).
   - Interactive hover glows, stroke scaling based on log-transformed incident volumes, and live filtering by category and pattern.

---

## 5. API Endpoints

### 5.1 Get Connection Map Topology
```http
GET /api/patterns/connection-map
```
Optional query parameters:
- `pattern_id`: Filter edges connected to a specific pattern (e.g. `PATTERN 04`).
- `category`: Filter edges connected to a specific category (e.g. `Property`).

**Response Schema:**
```json
{
  "title": "Behavioral Connection Map",
  "corpus_incident_count": 220663,
  "total_nodes": 15,
  "total_edges": 34,
  "nodes": [
    {
      "id": "cat_property",
      "label": "Property",
      "title": "Property Offenses (Theft, Burglary, Larceny, Motor Vehicle Theft)",
      "type": "crime_category",
      "incident_count": 111244,
      "percentage": 50.41,
      "color": "#0ea5e9"
    },
    {
      "id": "pattern_03",
      "label": "PATTERN 04",
      "title": "Nocturnal & Weekend Residential/Commercial Burglary",
      "type": "behavioral_pattern",
      "incident_count": 33335,
      "percentage": 8.24,
      "color": "#a855f7"
    }
  ],
  "edges": [
    {
      "id": "edge_cat_property_pattern_03",
      "source": "cat_property",
      "target": "pattern_03",
      "source_label": "Property",
      "target_label": "PATTERN 04",
      "incident_count": 33065,
      "percentage_of_pattern": 99.2,
      "percentage_of_category": 29.7,
      "similarity_score": 76.2,
      "strength_label": "Dominant Core Link",
      "shared_behavioral_dna": {
        "time": "Nocturnal concentration (48.1% nighttime execution, 77.0% weekend)",
        "location": "Small municipal or suburban jurisdiction",
        "property": "Targeted property acquisition (99.2% involved, mean loss: $3,240)",
        "weapon": "Unarmed / minimal weapon brandishing (98.35% unarmed)",
        "context_harm": "Physical injury: 1.57%, on-scene arrest rate: 9.38%",
        "key_shared_traits": [
          "Nocturnal timing pattern",
          "Weekend concentration",
          "Property acquisition objective",
          "Unarmed execution"
        ],
        "why_connected": "Incidents in 'Property' connect to 'PATTERN 04' because 33,065 historical cases share identical operational DNA..."
      }
    }
  ],
  "ethical_advisory": "The Behavioral Connection Map represents shared behavioral characteristics (modus operandi) between crime categories and behavioral patterns discovered in historical data. It does NOT represent people, suspects, offenders, identities, or criminal networks."
}
```

### 5.2 Alias Route
```http
GET /api/cross-crime/connection-map
```
Provides backward compatibility under the cross-crime routing namespace.

---

## 6. Verification & Automated Testing

- **Graph Generation Tests**: `tests/test_behavioral_connection_map.py`
  - Validates dynamic generation of all nodes and 34 edges.
  - Asserts non-zero incident counts summing to corpus volume.
  - Verifies presence and contents of `SharedBehavioralDna` (Time, Location, Property, Weapon, Context).
  - Asserts strict presence of non-offender and non-network ethical disclaimers.
  - Tests API endpoints and dynamic filtering by category and pattern.
- **Frontend Verification**:
  - `tsc -b && vite build` compiles cleanly with zero errors.
