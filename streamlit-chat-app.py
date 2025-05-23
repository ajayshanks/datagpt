import time
import streamlit as st
import requests
import json
import pandas as pd

# Configure the page to use wide layout
st.set_page_config(layout="wide")


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

def generate_sample_step4_data():
    """Generate sample data for step 4 when the webhook fails"""
    return {
        "summary": "Sample summary of findings for the data fitness check.",
        "missing_attributes": [
            {
                "table_name": "stg_sample_table",
                "column_name": "sample_column",
                "importance": "High",
                "impact": "Cannot calculate key metrics without this data"
            },
            {
                "table_name": "stg_sample_table",
                "column_name": "another_column",
                "importance": "Medium",
                "impact": "Reduces accuracy of segmentation"
            }
        ]
    }

def generate_sample_step5_data():
    """Generate sample data for step 5 when the webhook fails"""
    return {
        "parsed": {
            "data_quality_rules": [
                {
                    "table_name": "stg_iqvia_xpo_rx", 
                    "column_name": "product_id",
                    "rule_name": "NOT_NULL",
                    "configuration_information": "Column must not contain NULL values"
                },
                {
                    "table_name": "stg_semarchy_cm_pub_m_hcp_profile", 
                    "column_name": "hcp_id",
                    "rule_name": "UNIQUE",
                    "configuration_information": "Values must be unique"
                },
                {
                    "table_name": "stg_zip_territory", 
                    "column_name": "zip_code",
                    "rule_name": "FORMAT_CHECK",
                    "configuration_information": "Must match pattern: '\\d{5}'"
                }
            ]
        }
    }

def generate_sample_step6_data():
    """Generate sample data for step 6 when the webhook fails"""
    return [
        {
            "integration_table_name": "int_sales_retail",
            "primary_source_staging_table": "stg_iqvia_xpo_rx",
            "secondary_source_staging_table": "stg_zip_territory",
            "mapping": [],
            "sql_query": "SELECT * FROM stg_iqvia_xpo_rx JOIN stg_zip_territory ON zip_code = territory_code",
            "justification": "This mapping combines sales data with territory information for retail analysis"
        },
        {
            "integration_table_name": "int_hcp_profile",
            "primary_source_staging_table": "stg_semarchy_cm_pub_m_hcp_profile",
            "secondary_source_staging_table": "stg_semarchy_cm_pub_x_hcp_address",
            "mapping": [],
            "sql_query": "SELECT * FROM stg_semarchy_cm_pub_m_hcp_profile JOIN stg_semarchy_cm_pub_x_hcp_address ON hcp_id = hcp_id",
            "justification": "This mapping combines HCP profile data with address information"
        }
    ]

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
    data_sources = st.session_state.get("last_payload", {}).get("data_sources", [])
    table_names = [f"stg_{source}" for source in data_sources]
    payload = {"table_name": table_names}

    st.session_state.step3_payload = payload
    st.session_state.current_step = 3
    st.session_state.step3_loading = True
    st.rerun()

def proceed_to_step4():
    webhook_url_step4 = "https://ajayshanks.app.n8n.cloud/webhook-test/4d5e6f7g-8h9i-10j11-12k13-14l15m16n17o"
    bearer_token_step4 = "datagpt@123"

    # Get data from session state
    data_sources = st.session_state.get("last_payload", {}).get("data_sources", [])
    table_names = [f"stg_{source}" for source in data_sources]
    use_case = st.session_state.get("last_payload", {}).get("use_case", "")
    business_rules = st.session_state.get("last_payload", {}).get("business_rules", [])

    # Prepare payload for step 4 as per the specified schema
    payload = [{
        "table_name": table_names,
        "usecase_name": use_case,
        "business_rules": business_rules
    }]

    st.session_state.step4_payload = payload

    try:
        headers = {
            "Authorization": f"Bearer {bearer_token_step4}",
            "Content-Type": "application/json"
        }
        
        st.info(f"Sending request to Step 4 webhook with payload: {payload}")
        
        # Set current step to 4 immediately to show the loading state
        st.session_state.current_step = 4
        st.session_state.step4_loading = True
        st.rerun()
    except Exception as e:
        st.error(f"Exception preparing Step 4 webhook call: {str(e)}")
        # For demonstration, use sample data when there's an error
        st.session_state.step4_response = generate_sample_step4_data()
        st.session_state.current_step = 4
        st.rerun()

def proceed_to_step5():
    webhook_url_step5 = "https://ajayshanks.app.n8n.cloud/webhook-test/12f6bf3b-f2dd-4ef3-bbe4-1746a1290e36"
    bearer_token_step5 = "datagpt@123"

    # Use the same payload as Step 3
    payload = st.session_state.get("step3_payload", {})

    st.session_state.step5_payload = payload

    try:
        headers = {
            "Authorization": f"Bearer {bearer_token_step5}",
            "Content-Type": "application/json"
        }
        
        st.info(f"Sending request to Step 5 webhook with payload: {payload}")
        
        # Set current step to 5 immediately to show the loading state
        st.session_state.current_step = 5
        st.session_state.step5_loading = True
        st.rerun()
    except Exception as e:
        st.error(f"Exception preparing Step 5 webhook call: {str(e)}")
        # For demonstration, use sample data when there's an error
        st.session_state.step5_response = generate_sample_step5_data()
        st.session_state.current_step = 5
        st.rerun()

def proceed_to_step6():
    webhook_url_step6 = "https://ajayshanks.app.n8n.cloud/webhook-test/c50d562c-05e5-4dc8-97bc-b9cd286e3d67"
    bearer_token_step6 = "datagpt@123"

    # Use the same payload as Step 5
    payload = st.session_state.get("step5_payload", {})

    st.session_state.step6_payload = payload

    try:
        headers = {
            "Authorization": f"Bearer {bearer_token_step6}",
            "Content-Type": "application/json"
        }
        
        st.info(f"Sending request to Step 6 webhook with payload: {payload}")
        
        # Set current step to 6 immediately to show the loading state
        st.session_state.current_step = 6
        st.session_state.step6_loading = True
        st.rerun()
    except Exception as e:
        st.error(f"Exception preparing Step 6 webhook call: {str(e)}")
        # For demonstration, use sample data when there's an error
        st.session_state.step6_response = generate_sample_step6_data()
        st.session_state.current_step = 6
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
    st.markdown("## Step 3: Profiling and Tagging")

    # Initial loading state - calling webhook to get uniqueID
    if st.session_state.get("step3_loading", False) and "step3_unique_id" not in st.session_state:
        with st.spinner("Getting unique ID from webhook..."):
            webhook_url_step3 = "https://ajayshanks.app.n8n.cloud/webhook-test/2a51622b-8576-44e0-911d-c428c6533bc8"
            bearer_token_step3 = "datagpt@123"
            payload = st.session_state.get("step3_payload", {})

            try:
                headers = {
                    "Authorization": f"Bearer {bearer_token_step3}",
                    "Content-Type": "application/json"
                }
                response = requests.post(webhook_url_step3, json=payload, headers=headers, timeout=180)
                
                if response.status_code == 200 and response.text.strip():
                    try:
                        # Assuming webhook returns {"uniqueID": "some-unique-id"}
                        unique_id_response = response.json()
                        if "uniqueID" in unique_id_response:
                            st.session_state.step3_unique_id = unique_id_response["uniqueID"]
                            st.rerun()
                        else:
                            st.error("Webhook response doesn't contain uniqueID")
                            if st.button("Retry"):
                                st.rerun()
                            if st.button("Go back to Step 2"):
                                st.session_state.current_step = 2
                                st.session_state.step3_loading = False
                                st.rerun()
                    except json.JSONDecodeError:
                        st.error(f"Invalid JSON response from webhook: {response.text}")
                        if st.button("Retry"):
                            st.rerun()
                        if st.button("Go back to Step 2"):
                            st.session_state.current_step = 2
                            st.session_state.step3_loading = False
                            st.rerun()
                else:
                    st.error(f"Webhook returned an error status: {response.status_code} - {response.text}")
                    if st.button("Retry"):
                        st.rerun()
                    if st.button("Go back to Step 2"):
                        st.session_state.current_step = 2
                        st.session_state.step3_loading = False
                        st.rerun()
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                if st.button("Retry"):
                    st.rerun()
                if st.button("Go back to Step 2"):
                    st.session_state.current_step = 2
                    st.session_state.step3_loading = False
                    st.rerun()
        return

    # Secondary loading state - polling database for results
    if "step3_unique_id" in st.session_state and st.session_state.get("step3_loading", False):
        with st.spinner("Processing data... Fetching results from database"):
            try:
                # Define your PostgreSQL connection parameters
                # These should be stored securely in a production environment
                # Consider using st.secrets for secure storage
                db_host = "aws-0-ap-south-1.pooler.supabase.com"
                db_name = "postgres"
                db_user = "postgres.pguxhjesyiffkujrrqyq"
                db_password = "MfmoYcfS2n6CXkyw"
                db_port = "6543"  # Default PostgreSQL port
                
                # Create a connection to the PostgreSQL database
                conn = None
                unique_id = st.session_state.step3_unique_id
                
                # Import necessary library
                import psycopg2
                
                try:
                    conn = psycopg2.connect(
                        host=db_host,
                        database=db_name,
                        user=db_user,
                        password=db_password,
                        port=db_port
                    )
                    
                    # Create a cursor
                    cur = conn.cursor()
                    
                    # Execute SQL query to fetch results based on uniqueID
                    cur.execute(
                        "SELECT response_data FROM demo_datawarehouse.n8n_processing_results WHERE unique_id = %s AND status = 'COMPLETED' AND step = 'profiling'",
                        (unique_id,)
                    )
                    
                    # Fetch result
                    result = cur.fetchone()
                    
                    if result:
                        # If we have results, parse the JSON and store it
                        st.session_state.step3_response = json.loads(result[0])
                        st.session_state.step3_loading = False
                        st.rerun()
                    else:
                        # Check if we need to continue polling or if there's an error
                        cur.execute(
                            "SELECT status FROM demo_datawarehouse.n8n_processing_results WHERE unique_id = %s AND step = 'profiling'",
                            (unique_id,)
                        )
                        status_result = cur.fetchone()
                        
                        if status_result and status_result[0] == 'ERROR':
                            st.error("Processing failed. Please try again.")
                            if st.button("Retry"):
                                # Reset and restart
                                del st.session_state.step3_unique_id
                                st.rerun()
                            if st.button("Go back to Step 2"):
                                st.session_state.current_step = 2
                                st.session_state.step3_loading = False
                                del st.session_state.step3_unique_id
                                st.rerun()
                        else:
                            # Still processing, wait and then rerun to check again
                            time.sleep(5)  # Wait 5 seconds before polling again
                            st.rerun()
                
                finally:
                    # Close cursor and connection
                    if conn is not None:
                        if cur is not None:
                            cur.close()
                        conn.close()
            
            except Exception as e:
                st.error(f"Database error: {str(e)}")
                if st.button("Retry"):
                    st.rerun()
                if st.button("Go back to Step 2"):
                    st.session_state.current_step = 2
                    st.session_state.step3_loading = False
                    if "step3_unique_id" in st.session_state:
                        del st.session_state.step3_unique_id
                    st.rerun()
        return

    # If we get here, we are not in loading state
    
    # Check if we have the response data
    if "step3_response" not in st.session_state or not st.session_state.step3_response:
        st.warning("No data available from the webhook yet.")
        if st.button("Start Processing"):
            st.session_state.step3_loading = True
            st.rerun()
        if st.button("Go back to Step 2"):
            st.session_state.current_step = 2
            st.rerun()
        return

    st.markdown("### Review tags and summaries for each table and column")
    
    # Process the response data
    response_data = st.session_state.get("step3_response", None)

    if not response_data or not isinstance(response_data, dict) or "data" not in response_data:
        st.warning("No valid step3_response found.")
        return

    # Extract the actual list of table items
    table_items = response_data.get("data", [])
    
    # Create empty lists for table and column data
    table_data = []
    column_data = []

    for item in table_items:
        # Extract table name safely
        table_name = item.get("table_name") or item.get("staging_table_name", "Unknown")

        # Handle table data
        table_data.append({
            "table_name": table_name,
            "classification": item.get("classification", "Unknown"),
            "summary": item.get("summary", "No summary")
        })

        # Handle column data
        for tag in item.get("column_tags", []):
            column_data.append({
                "table_name": table_name,
                "column_name": tag.get("column_name", "Unknown"),
                "tag": tag.get("tag", ""),
                "description": tag.get("description", "No description")
            })

    # Display table data
    st.markdown("### Table Tags")
    if table_data:
        st.dataframe(pd.DataFrame(table_data))
    else:
        st.info("No table data available")

    # Display column data
    st.markdown("### Column Tags")
    if column_data:
        st.dataframe(pd.DataFrame(column_data))
    else:
        st.info("No column data available")
    
    # Navigation buttons
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back to Step 2"):
            st.session_state.current_step = 2
            st.rerun()
    with col2:
        if st.button("Proceed to Step 4"):
            proceed_to_step4()

def display_step4():
    st.title("Data to Insights Pipeline")
    st.markdown("### An AI-assisted approach to transform your data into actionable insights")
    st.markdown("## Step 4: Checking if Data Fit for Purpose")
    
    # Check if we're still loading (first time on this page)
    if st.session_state.get("step4_loading", False):
        with st.spinner("Processing..."):
            webhook_url_step4 = "https://ajayshanks.app.n8n.cloud/webhook-test/8173dcf8-6fc4-4507-9def-9ad61422001d"
            bearer_token_step4 = "datagpt@123"
            
            try:
                headers = {
                    "Authorization": f"Bearer {bearer_token_step4}",
                    "Content-Type": "application/json"
                }
                
                # Try to get actual response from webhook
                response = requests.post(
                    webhook_url_step4, 
                    json=st.session_state.step4_payload, 
                    headers=headers, timeout = 300
                )
                
                if response.status_code == 200:
                    if response.text.strip():
                        try:
                            st.session_state.step4_response = response.json()
                        except json.JSONDecodeError:
                            st.error(f"Invalid JSON response from webhook: {response.text}")
                            st.session_state.step4_response = generate_sample_step4_data()
                    else:
                        st.error("Webhook returned an empty response")
                        st.session_state.step4_response = generate_sample_step4_data()
                else:
                    st.error(f"Step 4 webhook failed: {response.status_code} - {response.text}")
                    st.session_state.step4_response = generate_sample_step4_data()
            except Exception as e:
                st.error(f"Exception during Step 4 webhook call: {str(e)}")
                st.session_state.step4_response = generate_sample_step4_data()
                
            # Mark loading as complete
            st.session_state.step4_loading = False
            st.rerun()
        return

    # Display the response data
    if "step4_response" not in st.session_state:
        st.warning("No response data available")
        return
    
    # Display Summary of Findings
    st.markdown("### Summary of Findings")

    response_data = st.session_state.step4_response
    if "parsed" in response_data:
        response_data = response_data["parsed"]

    summary = response_data.get("summary", "No summary available")
    st.info(summary)
    
    # Display Missing Attributes as a table
    st.markdown("### Missing Attributes")
    missing_attributes = response_data.get("missing_attributes", [])
    
    if missing_attributes:
        df = pd.DataFrame(missing_attributes)
        st.dataframe(df)
    else:
        st.success("No missing attributes found!")
    
    # Navigation buttons
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back to Step 3"):
            st.session_state.current_step = 3
            st.rerun()
    with col2:
        if st.button("Proceed to Step 5"):
            proceed_to_step5()

def display_step5():
    st.title("Data to Insights Pipeline")
    st.markdown("### An AI-assisted approach to transform your data into actionable insights")
    st.markdown("## Step 5: Data Quality Rule Recommendation")
    
    # Check if we're still loading (first time on this page)
    if st.session_state.get("step5_loading", False):
        with st.spinner("Processing..."):
            webhook_url_step5 = "https://ajayshanks.app.n8n.cloud/webhook-test/12f6bf3b-f2dd-4ef3-bbe4-1746a1290e36"
            bearer_token_step5 = "datagpt@123"
            
            try:
                headers = {
                    "Authorization": f"Bearer {bearer_token_step5}",
                    "Content-Type": "application/json"
                }
                
                # Try to get actual response from webhook
                response = requests.post(
                    webhook_url_step5, 
                    json=st.session_state.step5_payload, 
                    headers=headers, 
                    timeout=300
                )
                
                if response.status_code == 200:
                    if response.text.strip():
                        try:
                            st.session_state.step5_response = response.json()
                        except json.JSONDecodeError:
                            st.error(f"Invalid JSON response from webhook: {response.text}")
                            st.session_state.step5_response = generate_sample_step5_data()
                    else:
                        st.error("Webhook returned an empty response")
                        st.session_state.step5_response = generate_sample_step5_data()
                else:
                    st.error(f"Step 5 webhook failed: {response.status_code} - {response.text}")
                    st.session_state.step5_response = generate_sample_step5_data()
            except Exception as e:
                st.error(f"Exception during Step 5 webhook call: {str(e)}")
                st.session_state.step5_response = generate_sample_step5_data()
                
            # Mark loading as complete
            st.session_state.step5_loading = False
            st.rerun()
        return

    # Display the response data
    if "step5_response" not in st.session_state:
        st.warning("No response data available")
        return
    
    # Parse and display data quality rules
    response_data = st.session_state.step5_response
    
    # Handle the actual response format (array with parsed.data_quality_rules)
    data_quality_rules = None
    
    # First check if response is a list (as in your paste.txt)
    if isinstance(response_data, list) and len(response_data) > 0:
        if "parsed" in response_data[0] and "data_quality_rules" in response_data[0]["parsed"]:
            data_quality_rules = response_data[0]["parsed"]["data_quality_rules"]
    # Then try the format you're handling in your existing code
    elif "parsed" in response_data and "data_quality_rules" in response_data["parsed"]:
        data_quality_rules = response_data["parsed"]["data_quality_rules"]
    
    st.markdown("### Recommended Data Quality Rules")
    
    if data_quality_rules:
        # Create a DataFrame and ensure columns are in the specified order
        df = pd.DataFrame(data_quality_rules)
        
        # Reorder columns as requested
        column_order = ["table_name", "column_name", "rule_name", "configuration_information"]
        df = df[column_order]
        
        # Sort by table_name then column_name
        df = df.sort_values(by=["table_name", "column_name"])
        
        # Reset index
        df = df.reset_index(drop=True)
        
        st.dataframe(df)
    else:
        st.error("Response does not contain expected data quality rules format.")
        st.json(response_data)  # Show raw response for debugging
    
    # Navigation buttons
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back to Step 4"):
            st.session_state.current_step = 4
            st.rerun()
    with col2:
        if st.button("Proceed to Step 6"):
            proceed_to_step6()

def display_step6():
    st.title("Data to Insights Pipeline")
    st.markdown("### An AI-assisted approach to transform your data into actionable insights")
    st.markdown("## Step 6: Mapping Staging to Integration")
    
    # Initial loading state - calling webhook to get uniqueID
    if st.session_state.get("step6_loading", False) and "step6_unique_id" not in st.session_state:
        with st.spinner("Getting unique ID from webhook..."):
            webhook_url_step6 = "https://ajayshanks.app.n8n.cloud/webhook-test/c50d562c-05e5-4dc8-97bc-b9cd286e3d67"
            bearer_token_step6 = "datagpt@123"
            payload = st.session_state.get("step6_payload", {})

            try:
                headers = {
                    "Authorization": f"Bearer {bearer_token_step6}",
                    "Content-Type": "application/json"
                }
                response = requests.post(webhook_url_step6, json=payload, headers=headers, timeout=60)
                
                if response.status_code == 200 and response.text.strip():
                    try:
                        # Assuming webhook returns {"uniqueID": "some-unique-id"}
                        unique_id_response = response.json()
                        if "uniqueID" in unique_id_response:
                            st.session_state.step6_unique_id = unique_id_response["uniqueID"]
                            st.rerun()
                        else:
                            st.error("Webhook response doesn't contain uniqueID")
                            if st.button("Retry"):
                                st.rerun()
                            if st.button("Go back to Step 5"):
                                st.session_state.current_step = 5
                                st.session_state.step6_loading = False
                                st.rerun()
                    except json.JSONDecodeError:
                        st.error(f"Invalid JSON response from webhook: {response.text}")
                        if st.button("Retry"):
                            st.rerun()
                        if st.button("Go back to Step 5"):
                            st.session_state.current_step = 5
                            st.session_state.step6_loading = False
                            st.rerun()
                else:
                    st.error(f"Webhook returned an error status: {response.status_code} - {response.text}")
                    if st.button("Retry"):
                        st.rerun()
                    if st.button("Go back to Step 5"):
                        st.session_state.current_step = 5
                        st.session_state.step6_loading = False
                        st.rerun()
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                if st.button("Retry"):
                    st.rerun()
                if st.button("Go back to Step 5"):
                    st.session_state.current_step = 5
                    st.session_state.step6_loading = False
                    st.rerun()
        return

    # Secondary loading state - polling database for results
    if "step6_unique_id" in st.session_state and st.session_state.get("step6_loading", False):
        with st.spinner("Processing data... Fetching results from database"):
            try:
                # Define your PostgreSQL connection parameters
                # These should be stored securely in a production environment
                # Consider using st.secrets for secure storage
                db_host = "aws-0-ap-south-1.pooler.supabase.com"
                db_name = "postgres"
                db_user = "postgres.pguxhjesyiffkujrrqyq"
                db_password = "MfmoYcfS2n6CXkyw"
                db_port = "6543"  # Default PostgreSQL port
                
                # Create a connection to the PostgreSQL database
                conn = None
                unique_id = st.session_state.step6_unique_id
                
                # Import necessary library
                import psycopg2
                
                try:
                    conn = psycopg2.connect(
                        host=db_host,
                        database=db_name,
                        user=db_user,
                        password=db_password,
                        port=db_port
                    )
                    
                    # Create a cursor
                    cur = conn.cursor()
                    
                    # Execute SQL query to fetch results based on uniqueID
                    cur.execute(
                        "SELECT response_data FROM demo_datawarehouse.n8n_processing_results WHERE unique_id = %s AND status = 'COMPLETED' AND step = 'integration_mapping'",
                        (unique_id,)
                    )
                    
                    # Fetch result
                    result = cur.fetchone()
                    
                    if result:
                        # If we have results, parse the JSON and store it
                        st.session_state.step6_response = json.loads(result[0])
                        st.session_state.step6_loading = False
                        st.rerun()
                    else:
                        # Check if we need to continue polling or if there's an error
                        cur.execute(
                            "SELECT status FROM demo_datawarehouse.n8n_processing_results WHERE unique_id = %s AND step = 'integration_mapping'",
                            (unique_id,)
                        )
                        status_result = cur.fetchone()
                        
                        if status_result and status_result[0] == 'ERROR':
                            st.error("Processing failed. Please try again.")
                            if st.button("Retry"):
                                # Reset and restart
                                del st.session_state.step6_unique_id
                                st.rerun()
                            if st.button("Go back to Step 5"):
                                st.session_state.current_step = 5
                                st.session_state.step6_loading = False
                                del st.session_state.step6_unique_id
                                st.rerun()
                        else:
                            # Still processing, wait and then rerun to check again
                            time.sleep(5)  # Wait 5 seconds before polling again
                            st.rerun()
                
                finally:
                    # Close cursor and connection
                    if conn is not None:
                        if cur is not None:
                            cur.close()
                        conn.close()
            
            except Exception as e:
                st.error(f"Database error: {str(e)}")
                if st.button("Retry"):
                    st.rerun()
                if st.button("Go back to Step 5"):
                    st.session_state.current_step = 5
                    st.session_state.step6_loading = False
                    if "step6_unique_id" in st.session_state:
                        del st.session_state.step6_unique_id
                    st.rerun()
        return

    # If we get here, we are not in loading state
    
    # Check if we have the response data
    if "step6_response" not in st.session_state:
        st.warning("No response data available")
        if st.button("Start Processing"):
            st.session_state.step6_loading = True
            st.rerun()
        if st.button("Go back to Step 5"):
            st.session_state.current_step = 5
            st.rerun()
        return
    
    
    # Process the response data
    response_data = st.session_state.get("step6_response", None)

    if not response_data or not isinstance(response_data, dict) or "data" not in response_data:
        st.warning("No valid step6_response found.")
        return
    
    st.markdown("### Integration Table Mappings")
    
    if response_data:
        # Create a DataFrame with the required columns
        mapping_data = []
        for item in response_data["data"]:
            mapping_data.append({
                "Integration Table Name": item.get("integration_table_name", ""),
                "Primary Source Staging Table": item.get("primary_source_staging_table", ""),
                "Secondary Source Staging Table": item.get("secondary_source_staging_table", ""),
                "Justification": item.get("justification", ""),
                "SQL Query": item.get("sql_query", "")
            })
        
        if mapping_data:
            df = pd.DataFrame(mapping_data)
            st.dataframe(df)
        else:
            st.info("No mapping data was provided.")
    else:
        st.error("Response does not contain expected mapping data format.")
        st.json(response_data)  # Show raw response for debugging
    
    # Navigation button to go back
    st.markdown("---")
    if st.button("Back to Step 5"):
        st.session_state.current_step = 5
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
    elif st.session_state.current_step == 4:
        display_step4()
    elif st.session_state.current_step == 5:
        display_step5()
    elif st.session_state.current_step == 6:
        display_step6()

if __name__ == "__main__":
    main()
