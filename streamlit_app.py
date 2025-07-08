import streamlit as st
import requests
import json
import time

# For a production setup, your Flask API should be deployed to a public endpoint
# (e.g., Databricks Apps, Azure App Service, AWS Lambda/API Gateway, etc.).
FLASK_API_BASE_URL = "https://tvsmazoogappsbx03-ds-svcmateai.azurewebsites.net/" # Adjust this if your Flask app is on a different host/port

# Define the endpoint for generating pitches
PITCH_GENERATION_ENDPOINT = f"{FLASK_API_BASE_URL}/smr/segmentation/pitches"

# Define the list of available languages
LANGUAGES = ["English", "Hindi", "Tamil", "Telugu", "Marathi", "Bengali", "Kannada"]
DURATION = ["pitch_30s", "pitch_2min"]
# --- Streamlit UI ---
st.set_page_config(layout="centered", page_title="TVS Personalized Service Reminder")

st.title("TVS Personalized Service Reminder")

# Input for Registration Number
reg_no = st.text_input("Please Enter Vehicle Registration Number.", value="KA45EC0087", help="Vehicle Registration Number (e.g., KA45EC0087).")
selected_language = st.selectbox(
    "Select Language For Pitch:",
    LANGUAGES,
    index=0, # Default to English
    help="Choose the language in which you want the reminder pitch."
)
# Input for duration
selected_duration = st.selectbox(
    "Select Pitch's Duration:",
    DURATION,
    index=0, # Default to English
    help="Choose duration for pitch."
)
if st.button("🚀 Generate Pitch"):
    if not reg_no:
        st.error("Please enter a Registration Number.")
    else:
        # Construct the payload for the Flask API with reg_no and language
        payload = {
            "reg_no": reg_no,
            "lang": selected_language,
            "platform" : "personalized_pitch",
            "duration" : selected_duration
        }

        st.info(f"Sending request for Registration Number: {reg_no}, Language: {selected_language}...")

        try:
            response = requests.post(PITCH_GENERATION_ENDPOINT, json=payload)

            st.subheader("Response:")
            if response.status_code == 200:
                st.success("Pitch generated successfully!")
                res = response.json()
                
                # Displaying the response details
                st.markdown(f"**Customer name:** {res.get('customer_name', 'N/A')}")
                st.markdown(f"**Segment:** {res.get('segment_name', 'N/A')}")
                st.markdown(f"**Model:** {res.get('model', 'N/A')}")
                st.markdown(f"**Vehicle age:** {res.get('vehicle_age', 'N/A')} years")
                st.markdown(f"**Last service date:** {res.get('last_service_date', 'N/A')}")
                st.markdown(f"**Expected service date:** {res.get('expected_service_date', 'N/A')}")
                st.markdown("---")
                st.markdown("### Reminder pitches:")
                st.markdown(res.get('pitch', 'No pitch received.'))
            else:
                st.error(f"Error: Flask API returned status code {response.status_code}")
                st.write("Response Text:")
                st.write(response.text) # Display raw text for non-200 responses

        except requests.exceptions.ConnectionError as e:
            st.error(f"Connection Error: Could not connect to the Flask API at {FLASK_API_BASE_URL}. "
                     f"Please ensure your Flask app is running and accessible. Details: {e}")
            st.info("💡 **Troubleshooting Tip:** Check if your Flask app is active and listening on the correct host/port. "
                    "If running in Databricks, ensure the cluster is up and the Flask server cell is executing.")
        except json.JSONDecodeError:
            st.warning("Received a non-JSON response from the Flask API. Check API logs for errors.")
            st.code(response.text)
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

st.markdown("---")