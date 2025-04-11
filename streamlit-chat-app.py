import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime

# Set page config
st.set_page_config(page_title="Chat Application", page_icon="💬", layout="wide")

# Initialize session state for chat history if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

# Webhook URL
WEBHOOK_URL = "https://ajayshanks.app.n8n.cloud/webhook-test/8af9852f-dd3b-421f-831a-b4f1c78f737e"

# App title
st.title("Chat Application")

# Helper function to convert JSON to DataFrame
def json_to_dataframe(json_data):
    # Handle different JSON structures
    try:
        # If it's a list of dictionaries
        if isinstance(json_data, list) and all(isinstance(item, dict) for item in json_data):
            return pd.DataFrame(json_data)
        
        # If it's a dictionary with simple key-value pairs
        elif isinstance(json_data, dict):
            # Check if dictionary values are also dictionaries (nested)
            nested_dict = any(isinstance(v, dict) for v in json_data.values())
            
            if nested_dict:
                # For nested dictionaries, create a DataFrame with key-value pairs
                rows = []
                for key, value in json_data.items():
                    if isinstance(value, dict):
                        # For nested dictionaries, add multiple rows
                        for subkey, subvalue in value.items():
                            rows.append({"Key": f"{key}.{subkey}", "Value": str(subvalue)})
                    else:
                        rows.append({"Key": key, "Value": str(value)})
                return pd.DataFrame(rows)
            else:
                # For flat dictionaries
                return pd.DataFrame({"Key": list(json_data.keys()), "Value": [str(v) for v in json_data.values()]})
        
        # Fallback: convert to string representation
        return pd.DataFrame({"Response": [str(json_data)]})
    
    except Exception as e:
        return pd.DataFrame({"Error": [f"Could not convert to table: {str(e)}"]})

# Function to display JSON nicely
def display_json_response(response_data):
    st.write("**Webhook Response:**")
    
    if isinstance(response_data, (dict, list)):
        # Create tabs for different views
        tab1, tab2 = st.tabs(["Table View", "Raw JSON"])
        
        with tab1:
            df = json_to_dataframe(response_data)
            st.dataframe(df, use_container_width=True)
        
        with tab2:
            st.code(json.dumps(response_data, indent=2), language="json")
    else:
        # For non-JSON responses
        st.code(response_data)

# Function to send message to webhook and get response
def send_to_webhook(message_content):
    try:
        payload = {
            "message": message_content,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        response = requests.post(
            WEBHOOK_URL,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        
        if response.status_code == 200:
            try:
                # Try to parse the response as JSON
                response_data = response.json()
                return True, "Message sent successfully to webhook", response_data
            except:
                # If response is not JSON, return the text
                return True, "Message sent successfully to webhook", response.text
        else:
            return False, f"Failed to send message. Status code: {response.status_code}", None
            
    except Exception as e:
        return False, f"Error sending message to webhook: {str(e)}", None

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message.get("is_response") and message.get("response_data"):
            st.write(message["content"])
            display_json_response(message["response_data"])
        else:
            st.write(message["content"])
        st.caption(message["timestamp"])

# Chat input
if prompt := st.chat_input("Type a message..."):
    # Add user message to chat history
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.messages.append({"role": "user", "content": prompt, "timestamp": timestamp})
    
    # Display user message
    with st.chat_message("user"):
        st.write(prompt)
        st.caption(timestamp)
    
    # Send message to webhook
    success, response_message, webhook_response = send_to_webhook(prompt)
    
    # Display system response
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if success:
        response_content = f"✅ {response_message}"
        st.session_state.messages.append({
            "role": "assistant", 
            "content": response_content, 
            "timestamp": timestamp,
            "is_response": True,
            "response_data": webhook_response
        })
        
        with st.chat_message("assistant"):
            st.write(response_content)
            display_json_response(webhook_response)
            st.caption(timestamp)
    else:
        response_content = f"❌ {response_message}"
        st.session_state.messages.append({
            "role": "assistant", 
            "content": response_content, 
            "timestamp": timestamp
        })
        
        with st.chat_message("assistant"):
            st.write(response_content)
            st.caption(timestamp)

# Add a button to clear chat history
if st.button("Clear Chat History"):
    st.session_state.messages = []
    st.rerun()

# Add some information about the app
with st.expander("About this app"):
    st.markdown("""
    This is a simple chat application that sends messages to a webhook URL and displays the response in a tabular format.
    
    **Features:**
    - Send and receive messages
    - View chat history
    - Messages are sent to a webhook for processing
    - Display the webhook's response in both table and raw JSON formats
    - Clear chat history with a button
    """)
