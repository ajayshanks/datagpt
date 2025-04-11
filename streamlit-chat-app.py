import streamlit as st
import requests
import json
from datetime import datetime

# Set page config
st.set_page_config(page_title="Chat Application", page_icon="💬")

# Initialize session state for chat history if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

# Webhook URL
WEBHOOK_URL = "https://ajayshanks.app.n8n.cloud/webhook-test/8af9852f-dd3b-421f-831a-b4f1c78f737e"

# App title
st.title("Chat Application")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        st.caption(message["timestamp"])

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
        response_content = f"✅ {response_message}\n\n**Webhook Response:**\n```\n{json.dumps(webhook_response, indent=2) if isinstance(webhook_response, (dict, list)) else webhook_response}\n```"
    else:
        response_content = f"❌ {response_message}"
    
    st.session_state.messages.append({"role": "assistant", "content": response_content, "timestamp": timestamp})
    
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
    This is a simple chat application that sends messages to a webhook URL and displays the response.
    
    **Features:**
    - Send and receive messages
    - View chat history
    - Messages are sent to a webhook for processing
    - Display the webhook's response
    - Clear chat history with a button
    """)
