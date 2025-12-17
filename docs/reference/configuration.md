# ⚙️ Configuration Reference

Configuration options for NFL RAI Analytics.

---

## 📊 Analysis Configuration

### FeatureEngineer

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `smooth_sigma` | 1.0 | 0.5-3.0 | Gaussian smoothing sigma for velocity/acceleration |

```python
from nfl_rai import FeatureEngineer

# Default
fe = FeatureEngineer(smooth_sigma=1.0)

# More smoothing (reduces noise)
fe = FeatureEngineer(smooth_sigma=2.0)

# Less smoothing (more sensitive)
fe = FeatureEngineer(smooth_sigma=0.5)
```

---

### RAICalculator

#### RTD Thresholds

| Role | Default | Recommended Range |
|------|---------|------------------|
| `defensive_coverage` | 4.0 | 3.0-5.0 |
| `targeted_receiver` | 3.0 | 2.0-4.0 |
| `pass_rush` | 5.0 | 4.0-6.0 |
| `default` | 5.0 | 4.0-6.0 |

```python
from nfl_rai import RAICalculator

calc = RAICalculator()

# Modify thresholds
calc.rtd_thresholds['defensive_coverage'] = 3.5
```

#### Component Weights

```python
# Default weights
weights = {
    'defensive_coverage': {
        'rtd': -0.25, 'te': 0.20, 'bpq': 0.05, 'cms': 0.35, 'sd': 0.15
    },
    'targeted_receiver': {
        'rtd': -0.20, 'te': 0.15, 'bpq': 0.35, 'cms': 0.05, 'sd': 0.25
    }
}

# Customize
calc.weights['defensive_coverage']['cms'] = 0.40
```

---

## 🖥️ Dashboard Configuration

### Streamlit Config (`.streamlit/config.toml`)

```toml
[server]
port = 8501
headless = true
enableCORS = true

[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#1A1D21"
textColor = "#FFFFFF"
font = "sans serif"

[browser]
gatherUsageStats = false
```

### Custom Port

```bash
streamlit run app.py --server.port 8080
```

---

## 📁 Output Configuration

### Default Directories

| Directory | Purpose | Configurable |
|-----------|---------|--------------|
| `outputs/figures/` | Visualization images | Yes |
| `outputs/reports/` | CSV exports | Yes |
| `outputs/videos/` | Play animations | Yes |

### Custom Output Directory

```python
from analysis.rai_analysis import RAIAnalysis

analysis = RAIAnalysis(output_dir='my_custom_output/')
```

---

## 🎬 Video Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `fps` | 10 | Frames per second |
| `format` | mp4 | Output format (mp4, gif) |
| `resolution` | 1400×700 | Video dimensions |

```python
from nfl_rai.video_generator import VideoGenerator

vg = VideoGenerator(fps=15)  # Higher frame rate
```

---

## 📈 Visualization Configuration

### Figure Sizes

| Chart Type | Default Size | Configurable |
|------------|--------------|--------------|
| Field plot | (14, 7) | Yes |
| Distribution | (10, 6) | Yes |
| Component breakdown | (12, 8) | Yes |
| Dashboard | (16, 12) | Yes |

```python
from nfl_rai.visualizations import NFLFieldPlotter

plotter = NFLFieldPlotter(figsize=(16, 9))  # Widescreen
```

### Color Schemes

```python
colors = {
    'field': '#2E7D32',    # Field green
    'offense': '#1565C0',   # Blue
    'defense': '#C62828',   # Red
    'ball': '#FF8F00',      # Orange
}
```

---

## 🔄 Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `NFL_DATA_DIR` | Data directory path | Current directory |
| `NFL_OUTPUT_DIR` | Output directory | `outputs/` |
| `STREAMLIT_PORT` | Dashboard port | 8501 |

```bash
export NFL_DATA_DIR=/path/to/data
python analysis/rai_analysis.py
```

---

## ⏭️ Next

- **[Troubleshooting](troubleshooting.md)** - Common issues
- **[FAQ](faq.md)** - Frequently asked questions
