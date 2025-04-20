import streamlit as st
import requests
import json

st.set_page_config(page_title="Data to Insights Pipeline", layout="wide")

# Apply Apple-style inspired white background and subtle styling
st.markdown("""
    <style>
    body {
        background-color: white !important;
        color: #1d1d1f;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    }
    .stTextArea textarea {
        background-color: #f9f9f9;
        border: 1px solid #dcdcdc;
    }
    .update-box {
        background-color: #fefefe;
        border: 1px solid #d0d0d0;
        border-radius: 8px;
        padding: 1em;
        margin-bottom: 1em;
    }
    .stButton>button {
        background-color: #0071e3;
        color: white;
        border-radius: 8px;
        padding: 0.5em 1em;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state for webhook responses
if 'processing_updates' not in st.session_state:
    st.session_state.processing_updates = {
        'Source Crawling': [],
        'Ingestion into Staging': []
    }

if 'last_payload' not in st.session_state:
    st.session_state.last_payload = {}

# Configuration (make this editable or externally configurable as needed)
CONFIG = {
    'Source Crawling': {
        'webhook_url': 'https://yourdomain.com/source-crawling-webhook',
        'bearer_token': 'your_token_here',
        'payload_template': lambda: st.session_state.last_payload
    },
    'Ingestion into Staging': {
        'webhook_url': 'https://yourdomain.com/ingestion-webhook',
        'bearer_token': 'your_token_here',
        'payload_template': lambda: st.session_state.last_payload
    }
}

st.title("Data to Insights Pipeline")
st.markdown("### Select your data and use case")

# Step 1 form
with st.form(key="data_insights_form"):
    data_sources = [
        "iqvia_xpo_rx", "semarchy_cm_pub_m_hcp_profile",
        "semarchy_cm_pub_x_address", "zip_territory",
        "semarchy_cm_pub_x_hcp_address"
    ]
    use_cases = ["Field Reporting", "IC Operations", "Segmentation"]

    selected_data_sources = st.multiselect("Select your data sources:", options=data_sources)
    selected_use_case = st.selectbox("Select your use case:", options=use_cases)

    st.subheader("Define your business rules:")
    if 'business_rules' not in st.session_state:
        st.session_state.business_rules = [""]

    business_rules = []
    for i, rule in enumerate(st.session_state.business_rules):
        rule_key = f"rule_{i}"
        business_rules.append(st.text_area(f"Rule {i+1}", value=rule, key=rule_key, height=100))

    submitted = st.form_submit_button(label="Submit")

if st.button("Add Another Business Rule"):
    st.session_state.business_rules.append("")
    st.rerun()

if submitted:
    if not selected_data_sources:
        st.error("Please select at least one data source.")
    elif not selected_use_case:
        st.error("Please select a use case.")
    else:
        business_rules = [rule for rule in business_rules if rule.strip()]
        payload = {
            "data_sources": selected_data_sources,
            "use_case": selected_use_case,
            "business_rules": business_rules
        }
        st.session_state.last_payload = payload
        st.success("Form submitted successfully!")
        st.json(payload)

st.markdown("---")
st.markdown("## Processing Updates")

# Section UI for each step in processing
for section, config in CONFIG.items():
    st.markdown(f"### {section}")
    col1, col2 = st.columns([2, 1])
    with col1:
        with st.container():
            st.markdown('<div class="update-box">', unsafe_allow_html=True)
            for update in st.session_state.processing_updates[section]:
                st.markdown(f"- {update}")
            st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        if st.button(f"Proceed to next step for {section}", key=f"btn_{section}"):
            try:
                headers = {
                    "Authorization": f"Bearer {config['bearer_token']}",
                    "Content-Type": "application/json"
                }
                response = requests.post(
                    config['webhook_url'],
                    json=config['payload_template'](),
                    headers=headers
                )
                if response.status_code == 200:
                    st.session_state.processing_updates[section].append(f"Triggered successfully: {response.text}")
                else:
                    st.session_state.processing_updates[section].append(f"Error: {response.status_code} - {response.text}")
            except Exception as e:
                st.session_state.processing_updates[section].append(f"Exception: {str(e)}")

# Simulated webhook response receiver (in reality, this would be a separate endpoint receiving POST requests)
# You could run this on a server to push responses into the app using e.g. server-sent events or polling a backend DB
# For demo purposes only:
if st.button("Simulate webhook response for Source Crawling"):
    st.session_state.processing_updates['Source Crawling'].append("Received update: Source crawling completed.")

if st.button("Simulate webhook response for Ingestion into Staging"):
    st.session_state.processing_updates['Ingestion into Staging'].append("Received update: Ingestion successful.")
