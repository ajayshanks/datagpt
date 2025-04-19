import streamlit as st
import requests
import json

def main():
    st.set_page_config(page_title="Data to Insights Pipeline", layout="wide")
    
    # App header
    st.title("Data to Insights Pipeline")
    st.markdown("### An AI-assisted approach to transform your data into actionable insights")
    
    # Step indicator
    st.markdown("## Step 1: Select your data and use case")
    
    # Updated data sources and use cases as provided
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
    
    # Webhook configuration
    webhook_url = "https://your-webhook-endpoint.com/api/data-insights"
    bearer_token = "YOUR_BEARER_TOKEN_HERE"  # Replace with actual token
    
    # Initialize business rules in session state if not present
    if 'business_rules' not in st.session_state:
        st.session_state.business_rules = [""]
    
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
        
        # Form submission buttons - make sure these are inside the form
        col1, col2 = st.columns(2)
        submit_button = col1.form_submit_button(label="Submit")
        reset_button = col2.form_submit_button(label="Reset")
    
    # Add button for new rule RIGHT AFTER the form
    # This ensures it appears below the business rules but before form processing
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
            
            # Send data to webhook
            try:
                headers = {
                    "Authorization": f"Bearer {bearer_token}",
                    "Content-Type": "application/json"
                }
                
                # Comment out the actual POST request during testing
                # response = requests.post(webhook_url, json=payload, headers=headers)
                # if response.status_code == 200:
                #     st.success(f"Data successfully sent to webhook. Response: {response.text}")
                # else:
                #     st.error(f"Error sending data: {response.status_code} - {response.text}")
                
                # For demo, just show success message
                st.info("If connected to a real webhook, the data would be sent now.")
                
                # Here you would typically navigate to the next step
                st.markdown("### Proceeding to next step...")
                
            except Exception as e:
                st.error(f"An error occurred: {e}")
    
    if reset_button:
        st.session_state.business_rules = [""]
        st.rerun()
    
    # Footer with instructions
    st.markdown("---")
    st.markdown("Fill out the form above and click 'Submit' to continue to the next step.")

if __name__ == "__main__":
    main()
