import streamlit as st
import requests
import json
import time
import pandas as pd

st.set_page_config(page_title="Data to Insights Pipeline", layout="wide")

# Apply Apple-style inspired white background and subtle styling with animated loader
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
        color: black !important;
    }
    .update-box {
        background-color: #fefefe;
        border: 1px solid #d0d0d0;
        border-radius: 8px;
        padding: 1em;
        margin-bottom: 1em;
    }
    .loader {
        display: inline-block;
        width: 1.2em;
        height: 1.2em;
        border-radius: 50%;
        animation: blink 1.4s infinite ease-in-out both;
        background-color: #0071e3;
    }
    @keyframes blink {
        0%, 80%, 100% {
            transform: scale(0);
        } 40% {
            transform: scale(1);
        }
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

if 'processing_flags' not in st.session_state:
    st.session_state.processing_flags = {
        'Source Crawling': False,
        'Ingestion into Staging': False
    }

# Configuration (make this editable or externally configurable as needed)
CONFIG = {
    'Source Crawling': {
        'webhook_url': 'https://ajayshanks.app.n8n.cloud/webhook-test/b058b9af-2a5d-4b61-ba29-3522902ba6c3',
        'bearer_token': 'datagpt@123',
        'payload_template': lambda: st.session_state.last_payload
    },
    'Ingestion into Staging': {
        'webhook_url': 'https://ajayshanks.app.n8n.cloud/webhook-test/0cfd6c96-9c7c-46aa-8a58-30b11b499172',
        'bearer_token': 'datagpt@123',
        'payload_template': lambda: st.session_state.last_payload
    }
}

st.title("Data to Insights Pipeline")
st.markdown("### Select your data, use case and business rules")

# Select data and use case and business rules form
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

if st.button("Reset Form"):
    st.session_state.business_rules = [""]
    st.session_state.processing_updates = {
        'Source Crawling': [],
        'Ingestion into Staging': []
    }
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

        # Trigger Source Crawling webhook
        section = 'Source Crawling'
        config = CONFIG[section]
        st.session_state.processing_flags[section] = True
        st.session_state.processing_updates[section].append({"status": "processing"})
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
            st.session_state.processing_flags[section] = False
            try:
                response_data = response.json()
                st.session_state.processing_updates[section][-1] = response_data
            except:
                st.session_state.processing_updates[section][-1] = {"raw": response.text}
        except Exception as e:
            st.session_state.processing_flags[section] = False
            st.session_state.processing_updates[section][-1] = {"error": str(e)}

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
                if isinstance(update, dict):
                    try:
                        df = pd.json_normalize(update)
                        st.dataframe(df, use_container_width=True)
                    except Exception as e:
                        st.markdown(f"Raw JSON: {json.dumps(update)}")
                else:
                    st.markdown(f"- {update}", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        if st.button(f"Proceed to next step for {section}", key=f"btn_{section}"):
            st.session_state.processing_flags[section] = True
            st.session_state.processing_updates[section].append({"status": "processing"})
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
                st.session_state.processing_flags[section] = False
                try:
                    response_data = response.json()
                    st.session_state.processing_updates[section][-1] = response_data
                except:
                    st.session_state.processing_updates[section][-1] = {"raw": response.text}
            except Exception as e:
                st.session_state.processing_flags[section] = False
                st.session_state.processing_updates[section][-1] = {"error": str(e)}
