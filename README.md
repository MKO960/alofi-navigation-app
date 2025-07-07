# Alofi Sustainability Navigation

This is a smart, AI-powered routing app designed for sustainable urban mobility. It calculates five diverse routes using real transport network data and presents travel time, CO₂ emissions, ventilation scores, and an overall sustainability score — all on a fullscreen interactive map.

---

## 🚀 Features

- 📍 Start and end point selection
- 🛣️ Generates 5 diverse alternative routes
- ⏱️ Travel time displayed
- 🌱 CO₂ emissions calculator
- 🌬️ Ventilation penalty detection
- 🌍 Fullscreen map using Folium
- 🧠 AI-inspired penalty system for smart routing

---

## 🛠 Requirements

Install dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

## ▶️ How to Run

After setting up the environment:

```bash
python reconstruct_file.py  # Rebuild the .pkl file
streamlit run app.py        # Launch the app
```

Then open the provided local URL to use the web interface.
```
---

## 📦 Large File Setup: vienna_networks.pkl

GitHub has a 25MB file size limit, so the `vienna_networks.pkl` file was split into chunks.

### 🔧 Reconstruct the Original File:
Run the following command:

```bash
python reconstruct_file.py
```

This will:
- Rebuild `vienna_networks.pkl` from the `.chunk` files
- Automatically verify file size and integrity

### 🔩 Included Files:
- `vienna_networks_part_01.chunk`
- `vienna_networks_part_02.chunk`
- `vienna_networks_manifest.txt`
- `reconstruct_file.py`
---

## 📁 Repository Contents

```
├── app.py                         # Streamlit app code
├── Vienna_AI_Base.ipynb          # Jupyter Notebook version
├── requirements.txt              # Required Python libraries
├── reconstruct_file.py           # Script to rebuild the .pkl file
├── split_file.py                 # Original file splitting script (optional)
├── vienna_networks_part_01.chunk
├── vienna_networks_part_02.chunk
├── vienna_networks_manifest.txt
```

---

## 👤 Author

Mohammed Alofi  
Master's Project – Smart & Sustainable Mobility  
KFUPM, 2025

---

## 📄 License

This project is for academic purposes only and not intended for commercial distribution.
