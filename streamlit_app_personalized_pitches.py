# streamlit_app.py
import streamlit as st
import requests
import json
import time


#
# For a production setup, your Flask API should be deployed to a public endpoint
# (e.g., Databricks Apps, Azure App Service, AWS Lambda/API Gateway, etc.).
FLASK_API_BASE_URL = "https://tvsmazoogappsbx03-ds-svcmateai.azurewebsites.net/" # Adjust this if your Flask app is on a different host/port

# Define the endpoint for generating pitches
PITCH_GENERATION_ENDPOINT = f"{FLASK_API_BASE_URL}/smr/segmentation/pitches"


# --- Streamlit UI ---
st.set_page_config(layout="centered", page_title="Flask API Interaction Demo")

st.title("TVS Personalized Service Reminder")


reg_no = st.text_input("Please Enter Vehicle Registration Number.", value="KA45EC0087", help="Vehicle Registration Number (entered as text).")
if st.button("🚀 Generate Pitch"):
    if not reg_no:
        st.error("Please enter a Registration Number.")
    else:
        # Construct the payload for the Flask API with only frame_no
        payload = {
            "reg_no": reg_no # frame_no is now the only key in the payload
        }

     

        try:
            response = requests.post(PITCH_GENERATION_ENDPOINT, json=payload)

            st.subheader("Response:")
            if response.status_code == 200:
                st.success("Pitch generated successfully!")
                #st.json(response.json()) 
                res = response.json()
                st.markdown(f"**Customer name:** {res['customer_name']}")
                st.markdown(f"**Segment:** {res['segment_name']}")
                st.markdown(f"**Model:** {res['model']}")
                st.markdown(f"**Vehicle age:** {res['vehicle_age']} years")
                st.markdown(f"**Last service date:** {res['last_service_date']}")
                #st.markdown(f"**Last interaction month:** {res['last_interaction_months']}")
                st.markdown(f"**Expected service date:** {res['expected_service_date']}")
                #st.markdown(f"**Registration number:** {res['registration_no']}")
                st.markdown("---")
                st.markdown("### Reminder pitches:")
                st.markdown(res['pitch'])
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
            st.warning("Received a non-JSON response from the Flask API.")
            st.code(response.text)
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

st.markdown("---")
