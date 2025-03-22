import streamlit as st
import os
import json
import pandas as pd
from datetime import datetime

# --- Config & Output Directory Setup ---
CONFIG_DIR = "configs"
OUTPUT_DIR = "outputs"
os.makedirs(CONFIG_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

st.set_page_config(page_title="🧠 Smart Web Crawler Assistant", layout="centered")
st.title("🧠 Smart Web Crawler Assistant")

st.markdown("""
This interface lets you configure a smart web scraping task. 
Submit your parameters below and save them as a config file for execution in Google Colab.
""")

# --- Input Section ---
with st.form("web_crawler_form"):
    prompt = st.text_input("Prompt", "Scrape latest laptops on Newegg with prices and ratings")
    url = st.text_input("Target URL", "https://www.newegg.com/laptops")
    filters = st.text_input("Filters (comma-separated)", "price, rating")
    submitted = st.form_submit_button("💾 Save Config")

    if submitted:
        config_data = {
            "task_type": "web_scraper",
            "prompt": prompt,
            "url": url,
            "filters": filters,
            "timestamp": datetime.now().isoformat()
        }
        filename = f"web_scraper_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(CONFIG_DIR, filename)
        with open(filepath, "w") as f:
            json.dump(config_data, f, indent=4)
        st.success(f"✅ Config saved as {filename}")

# --- Load Existing Configs ---
st.markdown("---")
st.subheader("📂 Load Previous Config")
config_files = sorted([f for f in os.listdir(CONFIG_DIR) if f.endswith('.json')], reverse=True)
selected_config = st.selectbox("Select a saved config", config_files)

if selected_config:
    with open(os.path.join(CONFIG_DIR, selected_config), 'r') as f:
        loaded_config = json.load(f)
    st.code(json.dumps(loaded_config, indent=2), language='json')

# --- Output Preview ---
st.markdown("---")
st.subheader("📄 Latest Output Preview")
latest_outputs = sorted([f for f in os.listdir(OUTPUT_DIR) if f.endswith('.csv')], reverse=True)

if latest_outputs:
    latest_file = latest_outputs[0]
    st.markdown(f"Showing latest output: `{latest_file}`")
    df = pd.read_csv(os.path.join(OUTPUT_DIR, latest_file))
    st.dataframe(df.head(10))
else:
    st.info("No output files found yet. Run the assistant in Colab to generate results.")
