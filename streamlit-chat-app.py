import time
import streamlit as st
import requests
import json
import pandas as pd


def generate_sample_step3_data(table_names):
    """Generate sample data for step 3 when the webhook fails"""
    sample_data = []
    
    for table_name in table_names:
        sample_item = {
            "table_name": table_name,
            "classification": "Sample Classification",
            "summary": f"This is a sample summary for {table_name}",
            "column_tags": [
                {
                    "column_name": "sample_column_1",
                    "tag": "PII",
                    "description": "Sample personal identifier"
                },
                {
                    "column_name": "sample_column_2",
                    "tag": "METRIC",
                    "description": "Sample metric data"
                }
            ]
        }
        sample_data.append(sample_item)
    
    return sample_data

def display_step1(on_submit_callback):
    # App header
    st.title("Data to Insights Pipeline")
    st.markdown("### An AI-assisted approach to transform your data into actionable insights")
    
    # Step indicator
    st.markdown("## Step 1: Select your data and use case")
    
    # Data sources and use cases
    data_sources = [
        "iqvia_xpo_rx", 
        "semarchy_cm_pub_m_hcp_profile", 
        "semarchy_cm_pub_x_address", 
        "zip_territory", 
        "semarchy_cm_pub_x_hcp_address"
    ]
    
    use_cases = [
        "Field Reporting",
        "IC Operations",
        "Segmentation"
    ]
    
    # Step 2 Webhook configuration
    webhook_url_step2 = "https://ajayshanks.app.n8n.cloud/webhook-test/0cfd6c96-9c7c-46aa-8a58-30b11b499172"
    bearer_token_step2 = "datagpt@123"  # Replace with actual token
    
    # Form creation
    with st.form(key="data_insights_form"):
        # 1. Multi-select dropdown for data sources
        selected_data_sources = st.multiselect(
            "Select your data sources:",
            options=data_sources
        )
        
        # 2. Single-select dropdown for use case
        selected_use_case = st.selectbox(
            "Select your use case:",
            options=use_cases
        )
        
        # 3. Business rules input - dynamic text boxes
        st.subheader("Define your business rules:")
        
        # Display existing business rule inputs
        business_rules = []
        for i, rule in enumerate(st.session_state.business_rules):
            rule_key = f"rule_{i}"
            business_rules.append(st.text_area(f"Rule {i+1}", value=rule, key=rule_key, height=100))
        
        # Form submission buttons
        submit_button = st.form_submit_button(label="Submit")
    
    # Add button for new rule RIGHT AFTER the form
    if st.button("Add Another Business Rule"):
        st.session_state.business_rules.append("")
        st.rerun()
    
    
    # Form processing
    if submit_button:
        if not selected_data_sources:
            st.error("Please select at least one data source.")
        elif not selected_use_case:
            st.error("Please select a use case.")
        else:
            # Clean up empty business rules
            business_rules = [rule for rule in business_rules if rule.strip()]
            
            # Prepare payload
            payload = {
                "data_sources": selected_data_sources,
                "use_case": selected_use_case,
                "business_rules": business_rules
            }
            
            # Display the JSON that would be sent
            st.success("Form submitted successfully!")
            st.json(payload)
            
            # Save the payload in session state for reference
            st.session_state.last_payload = payload
            
            # In a real application, send data to webhook
            try:
                headers = {
                    "Authorization": f"Bearer {bearer_token_step2}",
                    "Content-Type": "application/json"
                }
                
                response = requests.post(webhook_url_step2, json=payload, headers=headers)
                if response.status_code == 200:
                    st.session_state.webhook_response = response.json()
                else:
                    st.error(f"Error sending data: {response.status_code} - {response.text}")
                    return
                
                # Move to Step 2 immediately
                st.session_state.current_step = 2
                st.rerun()
                
            except Exception as e:
                st.error(f"An error occurred: {e}")

                if st.button("Proceed to Step 2"):
                    on_submit_callback()
    
    # Add a button to reset the form
    if st.button("Reset Form"):
        st.session_state.business_rules = [""]
        st.rerun()
    
    # Footer with instructions
    st.markdown("---")
    st.markdown("Fill out the form above and click 'Submit' to continue to the next step.")

def proceed_to_step3():
    webhook_url_step3 = "https://ajayshanks.app.n8n.cloud/webhook-test/2a51622b-8576-44e0-911d-c428c6533bc8"
    bearer_token_step3 = "datagpt@123"

    data_sources = st.session_state.get("last_payload", {}).get("data_sources", [])
    table_names = [f"stg_{source}" for source in data_sources]
    payload = {"table_name": table_names}

    st.session_state.step3_payload = payload

    try:
        headers = {
            "Authorization": f"Bearer {bearer_token_step3}",
            "Content-Type": "application/json"
        }
        
        st.info(f"Sending request to Step 3 webhook with payload: {payload}")
        response = requests.post(webhook_url_step3, json=payload, headers=headers)
        
        if response.status_code == 200:
            # Check if the response has content before parsing as JSON
            if response.text.strip():
                try:
                    st.session_state.step3_response = response.json()
                    st.session_state.current_step = 3
                    st.rerun()
                except json.JSONDecodeError as je:
                    st.error(f"Invalid JSON response from webhook: {response.text}")
                    st.error(f"JSON parsing error: {str(je)}")
            else:
                st.error("Webhook returned an empty response")
                # Use sample data for demonstration purposes
                st.session_state.step3_response = generate_sample_step3_data(table_names)
                st.session_state.current_step = 3
                st.rerun()
        else:
            st.error(f"Step 3 webhook failed: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"Exception during Step 3 webhook call: {str(e)}")
        # For demonstration, use sample data when there's an error
        st.session_state.step3_response = generate_sample_step3_data(table_names)
        if st.button("Continue with sample data"):
            st.session_state.current_step = 3
            st.rerun()

def display_step2():
    st.title("Data to Insights Pipeline")
    st.markdown("### An AI-assisted approach to transform your data into actionable insights")
    st.markdown("## Step 2: Crawling and Ingestion")

    # Initialize messages list if it doesn't exist
    if "step2_messages" not in st.session_state:
        st.session_state.step2_messages = []

    # Check if webhook response exists
    if 'webhook_response' not in st.session_state or not st.session_state.webhook_response:
        with st.spinner("Processing..."):
            progress = st.progress(0)
            for i in range(100):
                time.sleep(0.01)  # simulate delay
                progress.progress(i + 1)
        
        st.error("No data available from webhook response.")
        if st.button("Return to Step 1"):
            st.session_state.current_step = 1
            st.rerun()
        return

    # Process webhook response - handle both dict and list formats
    response = st.session_state.webhook_response
    
    # Display messages from the response
    st.success("Response received!")
    st.markdown("### Messages from Webhook")
    
    if isinstance(response, list):
        # Handle JSON array response
        for i, item in enumerate(response, 1):
            if isinstance(item, dict) and "message" in item:
                st.info(f"{i}. {item['message']}")
                # Add to message history if not already there
                if item["message"] not in st.session_state.step2_messages:
                    st.session_state.step2_messages.append(item["message"])
    elif isinstance(response, dict) and "message" in response:
        # Handle single object response
        st.info(response["message"])
        # Add to message history if not already there
        if response["message"] not in st.session_state.step2_messages:
            st.session_state.step2_messages.append(response["message"])
    else:
        st.warning("Webhook response does not contain expected format with 'message' field.")
        st.json(response)

    # Navigation buttons
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back to Step 1"):
            st.session_state.current_step = 1
            st.rerun()
    with col2:
        if st.button("Proceed to Step 3"):
            proceed_to_step3()

def display_step3():
    st.title("Data to Insights Pipeline")
    st.markdown("### An AI-assisted approach to transform your data into actionable insights")
    st.markdown("## Step 3: Profiling and Tagging")
    st.markdown("### Review tags and summaries for each table and column")

    if "step3_response" not in st.session_state or not st.session_state.step3_response:
        st.warning("No response from Step 3 webhook")
        return

    table_data = []
    column_data = []

    for item in st.session_state.step3_response:
        table_data.append({
            "table_name": item["table_name"],
            "classification": item["classification"],
            "summary": item["summary"]
        })
        for tag in item["column_tags"]:
            column_data.append({
                "table_name": item["table_name"],
                "column_name": tag["column_name"],
                "tag": tag["tag"],
                "description": tag["description"]
            })

    st.markdown("### Table Tags")
    st.dataframe(pd.DataFrame(table_data))

    st.markdown("### Column Tags")
    st.dataframe(pd.DataFrame(column_data))
    
    # Navigation buttons
    st.markdown("---")
    if st.button("Back to Step 2"):
        st.session_state.current_step = 2
        st.rerun()

def main():
    # Initialize session state for navigation
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 1
    
    # Initialize other session states if needed
    if 'business_rules' not in st.session_state:
        st.session_state.business_rules = [""]
    
    if 'webhook_response' not in st.session_state:
        # Initialize as None instead of using sample data
        st.session_state.webhook_response = None
    
    # Function to handle step transition
    def go_to_step_2():
        st.session_state.current_step = 2
    
    # Display the appropriate step
    if st.session_state.current_step == 1:
        display_step1(go_to_step_2)
    elif st.session_state.current_step == 2:
        display_step2()
    elif st.session_state.current_step == 3:
        display_step3()

if __name__ == "__main__":
    main()
