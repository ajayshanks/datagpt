import time
import streamlit as st
import requests
import json
import pandas as pd

def main():
    # Initialize session state for navigation
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 1
    
    # Initialize other session states if needed
    if 'business_rules' not in st.session_state:
        st.session_state.business_rules = [""]
    
    if 'webhook_response' not in st.session_state:
        # This would normally be empty and filled from the actual webhook response
        # For demonstration, we're pre-loading with sample data
        st.session_state.webhook_response = load_sample_data()
    
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
                
            except Exception as e:
                st.error(f"An error occurred: {e}")
    
    # Add a button to reset the form
    if st.button("Reset Form"):
        st.session_state.business_rules = [""]
        st.rerun()
    
    # Footer with instructions
    st.markdown("---")
    st.markdown("Fill out the form above and click 'Submit' to continue to the next step.")




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

    # Process webhook response
    response = st.session_state.webhook_response
    if isinstance(response, dict) and "message" in response:
        st.success("Response received!")
        st.markdown("### Message from Webhook")
        st.info(response["message"])
        
        # Add to message history if not already there
        if response["message"] not in st.session_state.step2_messages:
            st.session_state.step2_messages.append(response["message"])
    else:
        st.warning("Webhook response does not contain a 'message' field.")
        st.json(response)

    # Display message history if it exists
    if st.session_state.step2_messages and len(st.session_state.step2_messages) > 1:
        st.markdown("### Previous Webhook Responses:")
        for i, msg in enumerate(st.session_state.step2_messages[:-1], 1):
            st.info(f"{i}. {msg}")

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



def load_sample_data():
    # This function loads the sample data structure used for demonstration
    return json.loads('''[
  {
    "iqvia_xpo_rx": [
      {
        "column_name": "Prscrbr_Id",
        "data_type": "int8"
      },
      {
        "column_name": "Specialty_cd",
        "data_type": "int8"
      },
      {
        "column_name": "Plan_Id",
        "data_type": "text"
      },
      {
        "column_name": "Mkt_id",
        "data_type": "int8"
      },
      {
        "column_name": "Prod_Id",
        "data_type": "text"
      },
      {
        "column_name": "Product",
        "data_type": "text"
      },
      {
        "column_name": "Product Family",
        "data_type": "text"
      },
      {
        "column_name": "Channel_Id",
        "data_type": "int8"
      },
      {
        "column_name": "Pay_Type",
        "data_type": "int8"
      },
      {
        "column_name": "Product_Package_Id",
        "data_type": "int8"
      },
      {
        "column_name": "Time_Period_Id",
        "data_type": "text"
      },
      {
        "column_name": "Week_Cycle_Date",
        "data_type": "date"
      },
      {
        "column_name": "NRx_cnt",
        "data_type": "int8"
      },
      {
        "column_name": "RRx_cnt",
        "data_type": "int8"
      },
      {
        "column_name": "RRx_cost",
        "data_type": "int8"
      },
      {
        "column_name": "TRx_cnt",
        "data_type": "int8"
      },
      {
        "column_name": "TRx_cost",
        "data_type": "int8"
      },
      {
        "column_name": "Supplier_Id",
        "data_type": "int8"
      },
      {
        "column_name": "Product_Type",
        "data_type": "text"
      },
      {
        "column_name": "NBRx",
        "data_type": "int8"
      },
      {
        "column_name": "NBRx_qty",
        "data_type": "int8"
      },
      {
        "column_name": "New_Month_On_Therapy",
        "data_type": "int8"
      },
      {
        "column_name": "Total_Month_On_Therapy",
        "data_type": "int8"
      },
      {
        "column_name": "Source_System_Code",
        "data_type": "text"
      },
      {
        "column_name": "Effective_Start_Date",
        "data_type": "date"
      },
      {
        "column_name": "Effective_End_Date",
        "data_type": "date"
      },
      {
        "column_name": "Is_Active",
        "data_type": "int8"
      }
    ],
    "semarchy_cm_pub_m_hcp_profile": [
      {
        "column_name": "hcp_id",
        "data_type": "int8"
      },
      {
        "column_name": "hcp_create_date",
        "data_type": "timestamp"
      },
      {
        "column_name": "hcp_update_date",
        "data_type": "timestamp"
      },
      {
        "column_name": "hcp_provider",
        "data_type": "text"
      },
      {
        "column_name": "hcp_reg_hcp_id",
        "data_type": "text"
      },
      {
        "column_name": "hcp_salutation",
        "data_type": "text"
      },
      {
        "column_name": "hcp_first_name",
        "data_type": "text"
      },
      {
        "column_name": "hcp_middle_name",
        "data_type": "text"
      },
      {
        "column_name": "hcp_last_name",
        "data_type": "text"
      }
    ],
    "zip_territory": [
      {
        "column_name": "Zip",
        "data_type": "int8"
      },
      {
        "column_name": "Territory",
        "data_type": "int8"
      }
    ]
  }
]''')


if __name__ == "__main__":
    main()



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
        response = requests.post(webhook_url_step3, json=payload, headers=headers)
        if response.status_code == 200:
            st.session_state.step3_response = response.json()
            st.session_state.current_step = 3
            st.rerun()
        else:
            st.error(f"Step 3 webhook failed: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"Exception during Step 3 webhook call: {str(e)}")

def display_step3():
    st.title("Step 3: Profiling and Tagging")
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
