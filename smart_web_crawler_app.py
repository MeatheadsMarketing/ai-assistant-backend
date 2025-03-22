import streamlit as st
import os
import json
import pandas as pd
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# --- Page Config ---
st.set_page_config(page_title="🧠 Smart Web Crawler Assistant", layout="centered")
st.title("🧠 Smart Web Crawler Assistant")

# --- Upload Google Credentials ---
st.sidebar.subheader("🔐 Upload Google Credentials")
creds_file = st.sidebar.file_uploader("Upload your Google Drive client_secret.json", type="json")
if creds_file:
    with open("client_secret.json", "wb") as f:
        f.write(creds_file.read())

# --- Drive Upload Helper ---
def upload_to_drive(file_path, file_name):
    creds = service_account.Credentials.from_service_account_file(
        "client_secret.json", scopes=["https://www.googleapis.com/auth/drive.file"])
    service = build("drive", "v3", credentials=creds)
    file_metadata = {"name": file_name, "parents": ["root"]}
    media = MediaFileUpload(file_path, resumable=True)
    uploaded_file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    return f"https://drive.google.com/file/d/{uploaded_file['id']}/view"

# --- Save Config ---
st.markdown("## ✏️ Create New Config")
with st.form("web_crawler_form"):
    prompt = st.text_input("Prompt", "Scrape latest laptops on Newegg with prices and ratings")
    url = st.text_input("Target URL", "https://www.newegg.com/laptops")
    filters = st.text_input("Filters (comma-separated)", "price, rating")
    submitted = st.form_submit_button("💾 Save Config to Google Drive")

    if submitted:
        config_data = {
            "task_type": "web_scraper",
            "prompt": prompt,
            "url": url,
            "filters": filters,
            "timestamp": datetime.now().isoformat()
        }
        filename = f"smart_web_crawler_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w") as f:
            json.dump(config_data, f, indent=4)

        try:
            drive_link = upload_to_drive(filename, filename)
            st.success("✅ Config uploaded to Google Drive!")
            st.markdown(f"[📄 View on Google Drive]({drive_link})")
            st.markdown("---")
            st.markdown("### 📤 Run Assistant in Colab")
            colab_link = "https://colab.research.google.com/drive/YOUR_COLAB_NOTEBOOK_ID"
            st.markdown(f"[🚀 Open Assistant Notebook in Colab]({colab_link})")
        except Exception as e:
            st.error(f"❌ Upload failed: {e}")

# --- Output Preview ---
st.markdown("---")
st.subheader("📄 Latest Output Preview")
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)
latest_outputs = sorted([f for f in os.listdir(OUTPUT_DIR) if f.endswith('.csv')], reverse=True)
if latest_outputs:
    latest_file = latest_outputs[0]
    st.markdown(f"📁 Showing latest output: `{latest_file}`")
    df = pd.read_csv(os.path.join(OUTPUT_DIR, latest_file))
    st.dataframe(df.head(10))
    st.download_button("⬇️ Download CSV", df.to_csv(index=False), file_name=latest_file)
else:
    st.info("No output files found yet. Run the assistant in Colab to generate results.")

# --- Re-Run Last Config ---
st.markdown("---")
st.subheader("🔁 Re-Run Last Assistant")
if st.button("Re-Run Last Config in Colab"):
    colab_link = "https://colab.research.google.com/drive/YOUR_COLAB_NOTEBOOK_ID"
    st.markdown(f"[🚀 Open Assistant Notebook in Colab]({colab_link})")

# --- History Dashboard ---
st.markdown("---")
st.subheader("🗂️ Config & Output History")
CONFIG_DIR = "configs"
os.makedirs(CONFIG_DIR, exist_ok=True)
all_configs = sorted([f for f in os.listdir(CONFIG_DIR) if f.endswith('.json')], reverse=True)
all_outputs = sorted([f for f in os.listdir(OUTPUT_DIR) if f.endswith('.csv')], reverse=True)

st.markdown("### Saved Configs")
for cfg in all_configs:
    with open(os.path.join(CONFIG_DIR, cfg)) as f:
        cfg_data = json.load(f)
    with st.expander(cfg):
        st.json(cfg_data)
        st.download_button("⬇️ Download Config", json.dumps(cfg_data, indent=2), file_name=cfg)

st.markdown("### Saved Outputs")
for out in all_outputs:
    with st.expander(out):
        df = pd.read_csv(os.path.join(OUTPUT_DIR, out))
        st.dataframe(df.head(5))
        st.download_button("⬇️ Download CSV", df.to_csv(index=False), file_name=out)
