# 🔧 Troubleshooting Guide

Common issues and solutions for NFL RAI Analytics.

---

## 🚨 Installation Issues

### `ModuleNotFoundError: No module named 'nfl_rai'`

**Cause:** Running from wrong directory or package not in path.

**Solution:**
```bash
# Run from project root
cd /path/to/analytics-NFL

# Or add to Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/analytics-NFL"
```

---

### `pip install` fails with dependency errors

**Cause:** Conflicting package versions.

**Solution:**
```bash
# Create fresh virtual environment
python -m venv venv --clear
source venv/bin/activate
pip install -r requirements.txt
```

---

### `ImportError: scipy.ndimage` issues

**Cause:** Incompatible scipy version.

**Solution:**
```bash
pip install scipy>=1.10.0
```

---

## 📂 Data Loading Issues

### `FileNotFoundError: tracking_week_*.csv`

**Cause:** Data files not in expected location.

**Solution:**
```bash
# Verify data structure
ls train/
# Should show: tracking_week_1.csv, tracking_week_2.csv, ...

# If files are elsewhere, specify path:
loader = NFLDataLoader(data_dir='/actual/path/to/data')
```

---

### `KeyError: 'gameId'` or column not found

**Cause:** Data file format mismatch.

**Solution:**
1. Verify CSV column names match expected schema
2. Check for encoding issues: `pd.read_csv(file, encoding='utf-8')`
3. Verify no header row issues

---

### Out of memory when loading data

**Cause:** Loading too much data at once.

**Solution:**
```bash
# Use sample mode
python analysis/rai_analysis.py --sample 100

# Or load specific weeks only
python analysis/rai_analysis.py --weeks 1 2 3
```

---

## ⚙️ Analysis Issues

### Analysis runs very slowly

**Cause:** Processing full dataset without optimization.

**Solutions:**
1. Use `--sample` flag for testing
2. Skip video generation with `--no-video`
3. Close other applications to free memory

---

### RAI scores are all NaN

**Cause:** Missing required data fields or calculation errors.

**Debug:**
```python
# Check for missing data
print(df.isnull().sum())

# Verify features calculated
print(df[['vx', 'vy', 'jerk_magnitude']].head())
```

---

### `ZeroDivisionError` in efficiency calculations

**Cause:** Player didn't move (path_length = 0).

**Solution:** This is handled in code, but if occurring:
```python
# Add epsilon to prevent division by zero
path_efficiency = straight_line / max(path_length, 0.001)
```

---

## 📊 Visualization Issues

### Figures not saving

**Cause:** Output directory doesn't exist.

**Solution:**
```bash
mkdir -p outputs/figures
mkdir -p outputs/reports
mkdir -p outputs/videos
```

---

### Charts appear blank in dashboard

**Cause:** Data not loaded or filters too restrictive.

**Solution:**
1. Verify data files exist in `outputs/reports/`
2. Check filter selections aren't empty
3. Refresh browser page

---

### 3D field rendering issues

**Cause:** WebGL or browser compatibility.

**Solution:**
1. Try Chrome or Firefox (latest version)
2. Enable hardware acceleration in browser
3. Update graphics drivers

---

## 🖥️ Dashboard Issues

### Dashboard won't start

**Cause:** Streamlit not installed or port in use.

**Solution:**
```bash
# Install Streamlit
pip install streamlit

# Use different port if 8501 in use
streamlit run app.py --server.port 8502
```

---

### "No data to display" on pages

**Cause:** Analysis hasn't been run yet.

**Solution:**
```bash
# Run analysis first
python analysis/rai_analysis.py

# Then start dashboard
cd dashboard && streamlit run app.py
```

---

### Dashboard crashes when loading

**Cause:** Corrupted cache or oversized data.

**Solution:**
```bash
# Clear Streamlit cache
rm -rf ~/.streamlit/cache

# Or reset via UI: Menu > Clear cache
```

---

## 🎬 Video Generation Issues

### `OSError: [Errno 2] ffmpeg not found`

**Cause:** FFmpeg not installed (required for MP4).

**Solution:**
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from ffmpeg.org and add to PATH
```

---

### Video files are 0 bytes

**Cause:** Writer error or insufficient frames.

**Solution:**
1. Ensure play has multiple output frames
2. Check disk space
3. Try GIF format instead: `format='gif'`

---

## 🐛 Debug Mode

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Then run analysis
from analysis.rai_analysis import RAIAnalysis
analysis = RAIAnalysis()
analysis.run_full_analysis()
```

---

## 📞 Still Stuck?

1. **Check error message** carefully - often indicates exact issue
2. **Verify data** with `loader.summary_stats()`
3. **Test with sample** data first
4. **Review logs** in terminal output

---

## ⏭️ Next

- **[FAQ](faq.md)** - Frequently asked questions
- **[Configuration](configuration.md)** - Adjust settings
