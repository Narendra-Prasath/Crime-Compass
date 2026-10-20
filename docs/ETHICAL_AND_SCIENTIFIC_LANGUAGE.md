# Ethical and Scientific Language Standard: CRIME DNA

## 1. Executive Summary & Foundational Principles

**CRIME DNA** is an unsupervised machine learning and statistical pattern analysis platform operating strictly on incident-level *modus operandi* (MO) characteristics. The system projects reported crime attributes onto a 70-dimensional behavioral feature space ($\mathbb{S}^{69} \subset \mathbb{R}^{70}$) to detect patterns and calculate mathematical similarities.

To ensure ethical integrity, scientific accuracy, and strict legal compliance, all user-facing interfaces, API schemas, algorithmic descriptions, tooltips, and technical documentation must adhere to rigorous terminology constraints.

### The Cardinal Rule

> **CRIME DNA analyzes behavioral patterns in historical incident data. Similarity or novelty does not establish offender identity, guilt, or causation.**
>
> Every user-facing analysis must explicitly state:
> **"Based on patterns learned from historical incidents."**

---

## 2. Terminology Mapping: Prohibited vs. Approved Language

The following matrix governs all system text across frontend components, backend responses, data models, and documentation:

| Prohibited Concept / Term | Scientifically Approved Replacement | Scientific & Legal Rationale |
| :--- | :--- | :--- |
| **Offender identification** | **Behavioral similarity** | Machine learning evaluates proximity between multi-attribute event vectors, not biological or personal identities. |
| **Person identification** | **Behavioral fingerprint** | Vectors represent situational and operational dynamics, not individual humans. |
| **Guilt / Culpability** | **Pattern fit / Modus operandi alignment** | Guilt is a judicial and constitutional determination reserved for courts of law, not a statistical metric. |
| **Criminality score** | **Behavioral intensity / Subprofile energy** | The system measures dimensional magnitude (e.g., property loss, temporal concentration), never intrinsic criminality. |
| **Future crime prediction** | **Historical behavioral pattern** | The engine identifies historical patterns across observed records; it never forecasts prospective criminal acts. |
| **Person risk prediction** | **Novel behavioral combination** | Outlier detection highlights statistically rare operational combinations in historical data, not dangerousness or risk. |
| **Same offender / Same perpetrator** | **Cross-crime behavioral similarity** | Multiple separate actors routinely employ identical methods due to opportunity structures or learned criminal tradecraft. |
| **Same criminal** | **Historical incident match** | Similarity connects incident events, not person entities. |
| **Criminal network / Gang linkage** | **Behavioral pattern topology / Shared MO clusters** | Graph nodes represent crime categories and unsupervised clusters, not organized crime networks or persons. |
| **Certainty from behavioral similarity** | **Statistical proximity / Cosine similarity** | High similarity scores indicate geometric closeness on a unit hypersphere, never conclusive linkage. |

---

## 3. Mandatory User-Facing Statements & Disclaimers

### 3.1. Standard Primary Disclaimer
Every user-facing analysis view, comparison drawer, and high-level analytical screen must display the following exact disclaimer in a visible but non-intrusive format:

```text
"CRIME DNA analyzes behavioral patterns in historical incident data. Similarity or novelty does not establish offender identity, guilt, or causation."
```

### 3.2. Mandatory Analysis Grounding Statement
Every result presentation (e.g., Level 1 Analysis Card, Incident History Record, Comparison Summary) must clearly declare:

```text
"Based on patterns learned from historical incidents."
```

### 3.3. Presentation Guidelines
- **Visibility:** Disclaimers must be rendered with high contrast and legible typography (e.g., styled with subtle shield icons and contextual borders).
- **Non-Intrusive:** Disclaimers must not obstruct interactive elements, navigation buttons, or data visualization canvases.
- **Persistent:** Topbar headers and footer summaries maintain persistent advisory notices across all application routes.

---

## 4. Mathematical & Scientific Justification

### 4.1. The Geometric Nature of Behavioral DNA
Each incident vector $\mathbf{x} \in \mathbb{R}^{70}$ is normalized to unit Euclidean length:
$$\|\mathbf{x}\|_2 = 1.000, \quad \mathbf{x} \in \mathbb{S}^{69}$$
Similarity between incident $\mathbf{a}$ and incident $\mathbf{b}$ is evaluated strictly via cosine similarity (equivalent to Euclidean dot product):
$$\text{Sim}(\mathbf{a}, \mathbf{b}) = \langle \mathbf{a}, \mathbf{b} \rangle = \sum_{i=1}^{70} a_i b_i$$

### 4.2. Why High Similarity Does Not Establish Common Identity
1. **Convergence on Tactical Opportunity:** Unrelated actors faced with similar environmental affordances (e.g., unlit alleyways, commercial storefronts during nighttime hours, cash-rich registers) naturally adopt analogous methods.
2. **Diffusion of Criminal Modus Operandi:** Common operational tactics diffuse through cultural knowledge, criminal networks, or public media. High behavioral similarity is consistent with completely independent actors.
3. **Absence of Forensic Uniqueness:** Unlike biological DNA, which exhibits unique polymorphic genetic alleles ($p < 10^{-15}$ random match probability), behavioral characteristics are low-entropy categorical indicators. High cosine similarity indicates shared situational characteristics, never forensic linkage.

### 4.3. Statistical Anomaly vs. Danger/Risk
Novelty scores produced by the Isolation Forest ensemble and centroid distance metrics ($d = 1 - \langle \mathbf{x}, \mathbf{c}_k \rangle$) identify **statistical rarity** (e.g., unusual property valuations, rare weapon combinations, atypical hours). An anomalous score indicates a *novel behavioral combination relative to learned historical distributions*, never human risk or prospective threat.

---

## 5. Architectural Implementation Across the Stack

### 5.1. Backend Service Layer
- **`analysis_engine.py`**: Embeds `ethical_advisory` in top-level output and `similar_behavioral_incidents`.
- **`comparison_service.py`**: Enforces strict non-attribution warnings in head-to-head incident comparisons.
- **`behavioral_graph_service.py`**: Declares that connection map edges link behavioral archetypes to crime categories, not humans or syndicates.
- **`novelty_service.py`**: Contextualizes novelty scores as statistical rarity within reference datasets.
- **`evolution_service.py`**: Clarifies that chronological shifts represent population-level aggregate trends, not serial tracking of single actors.

### 5.2. API Schema Layer (`src/api/schemas.py`)
All Pydantic response models (`AnalysisResponse`, `DnaComparisonResponse`, `SimilarityExplanationResponse`, `BehavioralConnectionMapResponse`, `NoveltyResponse`) provide explicit `ethical_advisory` and `disclaimer` fields initialized with approved wording.

### 5.3. Frontend Presentation Components
- **`App.tsx`**: Topbar features persistent scientific advisory notice.
- **`CrimeDnaResultExperience.tsx`**: Renders grounding phrase `"Based on patterns learned from historical incidents."` alongside prominent advisory banners.
- **`InputAnalysisPage.tsx`**: Labels input parameters objectively (e.g., "Reported Individuals Count" rather than prejudicial terminology).
- **`IncidentHistoryPage.tsx`**: Emphasizes isolated user storage and reference dataset boundary.
- **`BehavioralConnectionMapPage.tsx`**: Features bipartite network disclaimer forbidding person or gang attribution.

---

## 6. Continuous Enforcement & Verification

Automated test suites in `tests/` continuously audit backend and API responses to guarantee non-attribution compliance:
- `test_cross_crime_matching.py::test_ethical_boundary_compliance`
- `test_dna_comparison.py::test_ethical_non_offender_attribution`
- `test_behavioral_connection_map.py::test_ethical_and_non_offender_constraints`
- `test_novel_behavior_user_flow.py::test_ethical_advisory_compliance`

Any introduction of prohibited terminology into generated narratives or API schemas fails automated continuous integration checks.
