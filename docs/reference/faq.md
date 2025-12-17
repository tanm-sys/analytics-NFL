# ❓ Frequently Asked Questions

Common questions about NFL RAI Analytics.

---

## 📊 RAI Metric Questions

### What does RAI actually measure?

**RAI (Reactivity Advantage Index)** measures how well players react during the ball-in-air window after a pass is thrown. It combines:

- **Reaction speed** (how quickly they respond)
- **Movement efficiency** (how direct their path is)
- **Role-specific factors** (break quality for receivers, ball tracking for defenders)

---

### Why are some RAI scores negative?

RAI is normalized around 0 (league average). Scores can range from approximately -2 to +2:

| Score | Meaning |
|-------|---------|
| +1 to +2 | Well above average |
| 0 to +1 | Above average |
| -1 to 0 | Below average |
| -2 to -1 | Well below average |

---

### Why do defenders and receivers have different weights?

Different roles have different expectations:

- **Defenders** need to **react** to the ball and receiver (CMS weighted high)
- **Receivers** need to **execute** planned routes (BPQ weighted high)

The weights reflect what matters most for each role.

---

### What's a "good" RAI score?

| Percentile | RAI Score | Interpretation |
|------------|-----------|----------------|
| Top 10% | > 0.78 | Elite |
| Top 25% | > 0.65 | Above average |
| Average | 0.50-0.55 | Typical |
| Bottom 25% | < 0.42 | Below average |

---

## 🔧 Technical Questions

### How is reaction time detected?

Reaction is detected by monitoring **jerk** (rate of acceleration change). When jerk exceeds a threshold for 2+ consecutive frames, a reaction is recorded.

```
RTD = first frame where jerk > threshold for 2+ frames
```

---

### Why 10 Hz sampling rate?

NFL Next Gen Stats tracking data is collected at 10 Hz (10 samples per second). This is the standard NGS format.

---

### Can I adjust the component weights?

Yes! The weights are configurable:

```python
calc = RAICalculator()
calc.weights['defensive_coverage']['cms'] = 0.40  # Increase CMS weight
```

---

### Why does path efficiency sometimes exceed 1.0?

Due to numerical precision or smoothing effects, efficiency might slightly exceed 1.0. The code caps it at 1.0:

```python
efficiency = min(straight_line / path_length, 1.0)
```

---

## 📂 Data Questions

### How much data is needed?

| Analysis Type | Data Required |
|---------------|---------------|
| Testing | 1-3 weeks (~100 plays) |
| Analysis | 9+ weeks (~7,000 plays) |
| Full season | 18 weeks (~14,000 plays) |

---

### Can I use different seasons?

Yes, as long as the data format matches the expected schema. The code is season-agnostic.

---

### What if I'm missing some weeks?

The system handles missing weeks gracefully:

```python
loader.load_all_weeks(weeks=[1, 2, 3, 5, 6])  # Skip week 4
```

---

### How large are the data files?

| File Type | Size Per Week | Total (18 weeks) |
|-----------|---------------|------------------|
| Tracking | 50-100 MB | ~1.5 GB |
| Supplementary | - | ~7.5 MB |
| Output (RAI results) | - | ~5 MB |

---

## 🖥️ Dashboard Questions

### Why is the dashboard slow?

Common causes:
1. Large dataset (use filters)
2. 3D rendering (try 2D view)
3. Browser cache (clear cache)
4. Many browser tabs (close unused)

---

### Can I export data from the dashboard?

Yes! Most pages have download buttons for:
- CSV data exports
- PNG chart images
- PDF reports (on some pages)

---

### Does the dashboard require internet?

No. The dashboard runs entirely locally. However, some CDN-hosted fonts/icons may not load offline.

---

## 🏈 Football Questions

### Why focus on ball-in-air window?

This window (~0.5-2 seconds) is critical because:
1. Play outcome is being determined
2. Reactions matter most
3. Physical and cognitive skills combine

---

### What about pre-snap movement?

Current RAI focuses on post-snap, ball-in-air only. Pre-snap analysis could be added as a future extension.

---

### Does RAI account for route difficulty?

Not directly. A receiver running against elite coverage will have a harder time creating separation. Context should be considered when interpreting scores.

---

## 📈 Analysis Questions

### How long does full analysis take?

| Mode | Duration |
|------|----------|
| Sample (100 plays) | 2-5 minutes |
| Single week | 5-10 minutes |
| Full season (18 weeks) | 30-60 minutes |

---

### Can I run analysis in parallel?

Data loading is parallelized. RAI calculations are sequential for accuracy but optimized for speed.

---

### How do I add new metrics?

1. Add calculation method to `rai_calculator.py`
2. Include in composite formula
3. Update weights dictionary

---

## ⏭️ More Questions?

- Review the **[API Reference](../api-reference/data-loader.md)**
- Check **[Troubleshooting](troubleshooting.md)**
- Explore **[RAI Methodology](../architecture/rai-methodology.md)**
