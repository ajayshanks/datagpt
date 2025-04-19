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
    
    # Webhook configuration
    webhook_url = "https://ajayshanks.app.n8n.cloud/webhook-test/b058b9af-2a5d-4b61-ba29-3522902ba6c3"
    bearer_token = "datagpt@123"  # Replace with actual token
    
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
                    "Authorization": f"Bearer {bearer_token}",
                    "Content-Type": "application/json"
                }
                
               
                response = requests.post(webhook_url, json=payload, headers=headers)
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
    # App header
    st.title("Data to Insights Pipeline")
    st.markdown("### An AI-assisted approach to transform your data into actionable insights")
    
    # Step indicator
    st.markdown("## Step 2: Crawling and Ingestion")
    
    # Process the webhook response data
    if st.session_state.webhook_response:
        data = st.session_state.webhook_response
        
        # Create editable tables for each data source
        for dataset in data:
            for source_name, columns in dataset.items():
                st.subheader(f"Data Source: {source_name}")
                
                # Create DataFrame for editing
                df = pd.DataFrame(columns)
                
                # Initialize session state for this data source if not exists
                if f'edited_df_{source_name}' not in st.session_state:
                    st.session_state[f'edited_df_{source_name}'] = df.copy()
                
                # Create an editable dataframe
                edited_df = st.data_editor(
                    st.session_state[f'edited_df_{source_name}'],
                    key=f"editor_{source_name}",
                    use_container_width=True,
                    num_rows="fixed",
                    hide_index=True,
                    column_config={
                        "column_name": st.column_config.Column("Column Name", disabled=True),
                        "data_type": st.column_config.SelectboxColumn(
                            "Data Type",
                            options=["int8", "int", "float", "text", "varchar", "date", "timestamp", "boolean"],
                            required=True
                        )
                    }
                )
                
                # Update the session state with edited values
                st.session_state[f'edited_df_{source_name}'] = edited_df
        
        # Buttons for navigation
        col1, col2 = st.columns(2)
        
        # Back button to return to Step 1
        if col1.button("Back to Step 1"):
            st.session_state.current_step = 1
            st.rerun()
        
        # Submit button to send updated data
        if col2.button("Submit Updated Types"):
            # Prepare the updated JSON for webhook
            updated_data = []
            for dataset in data:
                updated_dataset = {}
                for source_name, _ in dataset.items():
                    if f'edited_df_{source_name}' in st.session_state:
                        # Convert DataFrame back to list of dicts
                        updated_dataset[source_name] = st.session_state[f'edited_df_{source_name}'].to_dict('records')
                updated_data.append(updated_dataset)
            
            st.success("Updated data types submitted successfully!")
            st.json(updated_data)
            
            webhook_url = "https://your-webhook-endpoint.com/api/data-insights/update-types"
            bearer_token = "YOUR_BEARER_TOKEN_HERE"
            
            # In a real application, send data to webhook
            try:
                headers = {
                    "Authorization": f"Bearer {bearer_token}",
                    "Content-Type": "application/json"
                }
                
                # Commented out for demo
                # response = requests.post(webhook_url, json=updated_data, headers=headers)
                # if response.status_code == 200:
                #     st.success(f"Data successfully updated. Response: {response.text}")
                # else:
                #     st.error(f"Error sending data: {response.status_code} - {response.text}")
                
                st.info("In a production environment, this would send the updated data types to the webhook.")
                
                # Here you would navigate to Step 3 if applicable
                # st.session_state.current_step = 3
                # st.rerun()
                
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.error("No data available from webhook response.")
        if st.button("Return to Step 1"):
            st.session_state.current_step = 1
            st.rerun()


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
