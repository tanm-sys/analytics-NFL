# 🏗️ System Overview

High-level architecture of the NFL RAI Analytics system.

---

## 🎯 System Purpose

The RAI Analytics system **quantifies player reaction quality** during the critical ball-in-air window after a pass is thrown. It transforms raw NFL tracking data into actionable insights for:

- 📊 **Player Evaluation** - Compare reaction capabilities across positions
- 🏈 **Game Planning** - Identify opponent weaknesses
- 🎓 **Training Programs** - Target specific improvement areas
- 📺 **Broadcast Analytics** - Real-time reaction visualization

---

## 🏛️ Architecture Layers

```mermaid
flowchart TB
    subgraph dataLayer["📥 DATA LAYER"]
        direction LR
        T1["Week 1"]
        T2["Week 2"]
        T3["..."]
        T18["Week 18"]
        SUPP["Supplementary<br/>Data"]
    end
    
    subgraph coreLayer["⚙️ CORE PROCESSING LAYER"]
        direction TB
        DL["📂 NFLDataLoader<br/>━━━━━━━━━━━━━<br/>• Load CSV files<br/>• Merge weeks<br/>• Standardize coordinates"]
        
        FE["📐 FeatureEngineer<br/>━━━━━━━━━━━━━<br/>• Velocity vectors<br/>• Acceleration<br/>• Path metrics"]
        
        RC["🎯 RAICalculator<br/>━━━━━━━━━━━━━<br/>• RTD, TE, BPQ<br/>• CMS, SD<br/>• Composite score"]
    end
    
    subgraph outputLayer["📊 OUTPUT LAYER"]
        direction LR
        VIZ["📈 Visualizations"]
        VID["🎬 Videos"]
        REP["📝 Reports"]
        DASH["🖥️ Dashboard"]
    end
    
    T1 --> DL
    T2 --> DL
    T3 --> DL
    T18 --> DL
    SUPP --> DL
    
    DL --> FE
    FE --> RC
    
    RC --> VIZ
    RC --> VID
    RC --> REP
    RC --> DASH
    
    style dataLayer fill:#1a365d,stroke:#3182ce,color:#fff
    style coreLayer fill:#22543d,stroke:#38a169,color:#fff
    style outputLayer fill:#553c9a,stroke:#805ad5,color:#fff
```

---

## 🔄 Processing Pipeline

```mermaid
graph LR
    subgraph stage1["Stage 1: Ingestion"]
        A1["Load 18 weeks<br/>of tracking"]
        A2["Load play<br/>metadata"]
        A3["Merge &<br/>validate"]
    end
    
    subgraph stage2["Stage 2: Processing"]
        B1["For each play"]
        B2["Extract input<br/>(pre-throw)"]
        B3["Extract output<br/>(post-throw)"]
        B4["Calculate<br/>features"]
    end
    
    subgraph stage3["Stage 3: Analysis"]
        C1["Calculate RAI<br/>components"]
        C2["Apply role<br/>weights"]
        C3["Generate<br/>composite"]
    end
    
    subgraph stage4["Stage 4: Output"]
        D1["Create<br/>visualizations"]
        D2["Export<br/>reports"]
        D3["Generate<br/>insights"]
    end
    
    A1 --> A2 --> A3
    A3 --> B1 --> B2 --> B3 --> B4
    B4 --> C1 --> C2 --> C3
    C3 --> D1 & D2 & D3
    
    style stage1 fill:#1a365d,stroke:#3182ce,color:#fff
    style stage2 fill:#2c5282,stroke:#4299e1,color:#fff
    style stage3 fill:#22543d,stroke:#38a169,color:#fff
    style stage4 fill:#553c9a,stroke:#805ad5,color:#fff
```

---

## 🧩 Component Responsibilities

### Data Layer

| Component | Responsibility | Input | Output |
|-----------|---------------|-------|--------|
| **Tracking Data** | Player positions at 10Hz | CSV files | Raw coordinates |
| **Supplementary** | Play context (formations, coverage) | CSV file | Play metadata |

### Core Layer

| Component | Responsibility | Input | Output |
|-----------|---------------|-------|--------|
| **NFLDataLoader** | Load, merge, standardize | CSV files | Unified DataFrame |
| **FeatureEngineer** | Physics calculations | Position data | Velocity, acceleration, jerk |
| **RAICalculator** | Compute RAI scores | Features | Component scores + composite |

### Output Layer

| Component | Responsibility | Input | Output |
|-----------|---------------|-------|--------|
| **RAIVisualizer** | Static plots | RAI scores | PNG figures |
| **VideoGenerator** | Play animations | Tracking data | MP4/GIF videos |
| **Reports** | Data export | RAI scores | CSV files |
| **Dashboard** | Interactive UI | All data | Web application |

---

## 📡 Data Flow Volumes

```mermaid
graph LR
    subgraph input["Raw Input"]
        IN["4.8M tracking records"]
    end
    
    subgraph process["Processing"]
        P1["562K output records"]
        P2["46K player-plays"]
        P3["14K plays"]
    end
    
    subgraph output["Results"]
        OUT["1.2K unique players<br/>with RAI scores"]
    end
    
    IN -->|"Filter post-throw"| P1
    P1 -->|"Group by player"| P2
    P2 -->|"Aggregate"| P3
    P3 -->|"Player profiles"| OUT
    
    style input fill:#c53030,stroke:#fc8181,color:#fff
    style process fill:#d69e2e,stroke:#ecc94b,color:#000
    style output fill:#38a169,stroke:#68d391,color:#fff
```

---

## 🔐 Key Design Principles

### 1. Role-Specific Processing

```mermaid
graph TD
    subgraph players["All Players"]
        P["Player Tracking Data"]
    end
    
    subgraph roles["Role Classification"]
        DEF["🛡️ Defenders<br/>High reactivity weight"]
        REC["🏃 Receivers<br/>High efficiency weight"]
        DL["⚔️ Pass Rush<br/>Physics constrained"]
    end
    
    subgraph weights["Weighted RAI"]
        W1["CMS +35%<br/>RTD -25%"]
        W2["BPQ +35%<br/>SD +25%"]
        W3["TE +35%<br/>RTD -35%"]
    end
    
    P --> DEF & REC & DL
    DEF --> W1
    REC --> W2
    DL --> W3
    
    style DEF fill:#3182ce,stroke:#63b3ed,color:#fff
    style REC fill:#38a169,stroke:#68d391,color:#fff
    style DL fill:#d53f8c,stroke:#f687b3,color:#fff
```

### 2. Temporal Separation

- **Input Data**: Pre-throw state (last frame before ball release)
- **Output Data**: Post-throw tracking (all frames during ball flight)
- **Window**: 0.5 - 2.0 seconds after release

### 3. Physics-Based Features

All derived features are grounded in kinematics:
- Velocity = ∂position/∂time
- Acceleration = ∂velocity/∂time
- Jerk = ∂acceleration/∂time (reaction indicator)

---

## 🛠️ Technology Stack

```mermaid
graph TB
    subgraph runtime["Runtime"]
        PY["Python 3.8+"]
    end
    
    subgraph data["Data Processing"]
        PD["pandas"]
        NP["numpy"]
        SP["scipy"]
    end
    
    subgraph viz["Visualization"]
        MPL["matplotlib"]
        SNS["seaborn"]
        PLT["plotly"]
    end
    
    subgraph dash["Dashboard"]
        ST["Streamlit"]
    end
    
    subgraph media["Media"]
        IO["imageio"]
    end
    
    PY --> PD & NP & SP
    PY --> MPL & SNS & PLT
    PY --> ST
    PY --> IO
    
    style runtime fill:#1a365d,stroke:#3182ce,color:#fff
    style data fill:#22543d,stroke:#38a169,color:#fff
    style viz fill:#553c9a,stroke:#805ad5,color:#fff
    style dash fill:#c53030,stroke:#fc8181,color:#fff
    style media fill:#d69e2e,stroke:#ecc94b,color:#000
```

---

## ⏭️ Next Steps

- **[Data Flow](data-flow.md)** - Detailed data pipeline
- **[RAI Methodology](rai-methodology.md)** - The science behind RAI
- **[Component Diagram](component-diagram.md)** - Class relationships
