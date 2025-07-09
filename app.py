
from flask import Flask, request, jsonify
import os, requests, random
import json
import pandas as pd
from databricks.sql import connect as databricks_connect
app = Flask('personalized_pitch')
DB_SERVER_HOSTNAME = os.getenv("DATABRICKS_SERVER_HOSTNAME")
DB_HTTP_PATH = os.getenv("DATABRICKS_HTTP_PATH")
DB_ACCESS_TOKEN = os.getenv("DATABRICKS_TOKEN")
def get_data_from_databricks(reg_no: str):
    query = f"SELECT * FROM vision_dev.sandbox.map_t_srv_mrkt_smr_all_dealers_daily_digi_app_july_2025_version_6_cluster WHERE REG_NO = '{reg_no}'"
    if not all([DB_SERVER_HOSTNAME, DB_HTTP_PATH, DB_ACCESS_TOKEN]):
        print("Databricks connection details not set in environment variables.")
        return None

    try:
        # CORRECT USAGE: Call the imported 'connect' function directly
        with databricks_connect(
            server_hostname=DB_SERVER_HOSTNAME,
            http_path=DB_HTTP_PATH,
            access_token=DB_ACCESS_TOKEN
        ) as connection:
            print("Successfully connected to Databricks SQL Warehouse.")
            with connection.cursor() as cursor:
                print(f"Executing query: {query}")
                cursor.execute(query)
                results = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                return pd.DataFrame(results, columns=columns)

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error querying Databricks: {e}")
        return None
def generate_pitch(customer_name: str, customer_care_executive: str, customer_segment: str, remaining_amc_services: float,
                   expected_service_type: str, last_interaction_months: int,
                   sale_series: str, customer_type: str,
                   endpoint: str, deployment: str, subscription_key: str, api_version: str, lang: str="English") -> str:
    base_prompt = """You are a helpful assistant trained to support Customer Care Executives (CCEs) at TVS Motor Company.
            These CCEs are typically 10th to 12th pass and speak to customers over the phone to remind them about upcoming or overdue vehicle services.
            Your job is to generate 5 simple, spoken-style pitch points that a CCE can use during a follow-up call to:
            Remind the customer that their vehicle service is due.
            Encourage them to book a service appointment.
            Highlight useful benefits that TVSM offers (to build interest and trust).
            How You Should Generate the Pitch:
            Use simple words, short sentences, and conversational tone.
            Mention TVSM benefits that are relevant to the customer, like:
            Free pick-up and drop for service
            AMC plans to reduce service cost
            Service by trained TVS technicians
            Quick repair services
            Use  relatable language (avoid complicated English).
            Be friendly, polite, and persuasive – like someone helping a neighbour"""
    


    headers = {
        "Content-Type": "application/json",
        "api-key": subscription_key
    }

    customer_details = (
        f"Customer Details: Vehicle Model: {sale_series}, "
        f"Customer Care Executive : {customer_care_executive}, "
        f"Expected Service: {expected_service_type}, "
        f"Remaining AMC Services: {remaining_amc_services}, "
        f"Last Interaction: {last_interaction_months} months ago, "
        f"Customer Type: {customer_type}."
    )


    segment_specific_guidance = {
        "Paid service skippers": (
            "Generate 5 key pitch points. Emphasize: long-term cost savings of proper maintenance (especially if {expected_service_type} service), "
            "safety benefits, maintaining vehicle warranty, preventing major breakdowns, and special offers for returning customers. "
            "Highlight the importance of servicing their {sale_series} to avoid bigger costs, especially if {last_interaction_months} is high. "
            "Mention any benefits of utilizing AMC if {remaining_amc_services} > 0."
            "Example start: 'Hi {customer_name}, this is {customer_care_executive} from TVS Motor Vehicle Service. We noticed your {sale_series} is due for its {expected_service_type} service. To help you ensure your vehicle stays reliable and cost-effective, here are a few points:'"
        ),
        "Free service maximisers": (
            "Generate 5 key pitch points. Focus on: the critical importance of paid services (if {expected_service_type} is Paid) beyond free ones for {sale_series} longevity, "
            "performance optimization, safety enhancements, protecting resale value, and addressing hidden wear and tear. "
            "Stress that a full service ensures all aspects of their {sale_series} are covered, not just free checks. "
            "Mention if they have {remaining_amc_services} paid AMC services remaining and how to utilize them."
            "Example start: 'Hi {customer_name}, this is {customer_care_executive} from TVS Motor Vehicle Service. We noticed your {sale_series} is due for its {expected_service_type} service. We appreciate you utilizing our free services, and to ensure your {sale_series}'s continued top performance, here are some key reminders:'"
        ),
        "Lapsed customers (Retail finance)": (
            "Generate 5 key pitch points. Emphasize: protecting their financed {sale_series} asset, maintaining vehicle value for loan tenure, "
            "avoiding potential issues that could affect loan terms, ensuring safety, and a complimentary check-up to identify any long-standing concerns given {last_interaction_months} months of no service. "
            "Highlight how service protects their investment and loan agreement."
            "Example start: 'Hi {customer_name}, this is {customer_care_executive} from TVS Motor Vehicle Service. We noticed your {sale_series} is due for its service. As a financed owner, protecting your investment is key, especially since it's been {last_interaction_months} months. Here are five important reasons to service your vehicle:'"
        ),
        "Lapsed customers (Cash)": (
            "Generate 5 key pitch points. Focus on: protecting their significant investment in their {sale_series}, ensuring long-term vehicle reliability, "
            "preventing costly breakdowns, maximizing resale value, and a comprehensive inspection to address any overlooked issues given {last_interaction_months} months of no service. "
            "Remind them that regular service safeguards their outright purchase."
            "Example start: 'Hi {customer_name}, this is {customer_care_executive} from TVS Motor Vehicle Service. We noticed your {sale_series} is due for its service. You've made a significant investment in your {sale_series}, and after {last_interaction_months} months, here are five key points to help protect it:'"
        ),
        "Routine maintainers": (
            "Generate 5 key pitch points. Acknowledge their excellent maintenance habits for their {sale_series}. Reinforce the ongoing benefits of consistent service, "
            "new service updates or checks available for {sale_series} (if any), maintaining peak performance, and prioritizing their safety and driving experience. "
            "Mention the value of their upcoming {expected_service_type} service and if they have {remaining_amc_services} AMC services left."
            "Example start: 'Hi {customer_name}, this is {customer_care_executive} from TVS Motor Vehicle Service. We noticed your {sale_series} is due for its {expected_service_type} service. As a diligent routine maintainer, you already know the value of timely service. Here are a few points for your upcoming visit:'"
        ),
        "Frequent service seekers": (
            "Generate 5 key pitch points. Validate their care for the {sale_series}, efficiency of combining minor checks into a full {expected_service_type} service, "
            "benefits of a comprehensive service, proactive prevention of major issues, and maximizing {sale_series} lifespan with expert care. "
            "Suggest how the current service can be comprehensive to address their concerns, especially if {remaining_amc_services} AMC services are available."
            "Example start: 'Hi {customer_name}, this is {customer_care_executive} from TVS Motor Vehicle Service. We noticed your {sale_series} is due for its {expected_service_type} service. We understand your dedication to your TVS {sale_series}, and here are five ways a comprehensive service can benefit you:'"
        )
    }

    full_prompt = (
        f"{base_prompt.format(customer_name=customer_name, dealer_name=customer_care_executive, sale_series=sale_series, last_interaction_months=last_interaction_months)} "
        f"{segment_specific_guidance.get(customer_segment, '').format(customer_name=customer_name, sale_series=sale_series, expected_service_type=expected_service_type, last_interaction_months=last_interaction_months, remaining_amc_services=remaining_amc_services)} "
        "Provide the 5 points in a concise, bulleted list format, suitable for a phone call. "
        "Don't combine sentance like 'Certainly! Here are five simple pitch points a Customer Care Executive can use during a follow-up call' in output. "
        "Translate pitch in {} language".format(lang)
    )


    data = {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": full_prompt}
        ],
        "temperature": 0.7, 
        "max_tokens": 300   
    }

    try:
        url = f"{endpoint}openai/deployments/{deployment}/chat/completions?api-version={api_version}"

        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx status codes)

        result = response.json()
        pitch = result['choices'][0]['message']['content'].strip()
        return pitch
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
        print(f"Response content: {response.text}") # Print raw response for detailed debugging
        return f"Error generating pitch due to an HTTP issue: {err}"
    except Exception as err:
        print(f"An unexpected error occurred: {err}")
        return f"An unexpected error occurred while generating the pitch: {err}"
def get_fallback_pitch(all_pitches_list, duration, language="English"):
    available_pitches_in_language = [
        entry.get(duration) for entry in all_pitches_list
        if entry.get('language') == language and duration in entry
    ]

    if available_pitches_in_language:
        return random.choice(available_pitches_in_language)
    else:
        return f"No random fallback pitch found for language '{language}'."

def load_pitches_from_json(file_path="reminder_pitches_30s_2mins_all_languages.json"):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('pitches', []) # Access the 'pitches' key which contains the list
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{file_path}'. Check file format.")
        return []
    except Exception as e:
        print(f"An unexpected error occurred while loading the JSON file: {e}")
        return []

def get_pitch(all_pitches_list, segment_name, language, pitch_type):
    # Ensure pitch_type is valid
    if pitch_type not in ["pitch_30s", "pitch_2min"]:
        return f"Invalid pitch_type: '{pitch_type}'. Must be 'pitch_30s' or 'pitch_2min'."

    for pitch_entry in all_pitches_list:
        if pitch_entry.get('segment') == segment_name and pitch_entry.get('language') == language:
            return pitch_entry.get(pitch_type, f"Pitch of type '{pitch_type}' not found for segment '{segment_name}' in '{language}'.")
    return f"Pitch not found for segment '{segment_name}' in '{language}'."

app = Flask('personalized_pitch')
@app.route('/', methods=['GET'])
def hello():
    return jsonify({"message": "Personalized service remainder running!!!!544"})
@app.route('/smr/segmentation/pitches', methods=['POST'])
def generate_personalized_pitches():
    data = request.get_json()
    reg_no = data['reg_no']
    lang = data['lang']  
    platform = data['platform']
    duration = data['duration']
    df = get_data_from_databricks(reg_no)
    pitch_dict = {}
    if len(df) == 0:
        pitches_data_list = load_pitches_from_json("reminder_pitches_30s_2mins_all_languages.json")
        pitch  = get_fallback_pitch(pitches_data_list,duration, lang)
        pitch_dict = { 
            'customer_name': "NA",
            'segment_name': "NA",
            'model': "NA",
            'vehicle_age': "NA",
            'last_service_date': "NA",
            'last_interaction_months': "NA",
            'expected_service_date': "NA",
            'registration_no': "NA",
            'pitch': pitch
            }
        print(pitch_dict)
        return jsonify(pitch_dict)
    customers_df = df[[
    "CUSTOMER_NAME",
    "DEALER_NAME",
    "segment_name",
    "REMAINING_AMC_SERVICES",
    "EXPECTED_SERVICE_TYPE",
    "LAST_INTERACTION",
    "SALE_SERIES",
    "CUSTOMER_TYPE",
    "VEHICLE_AGE_YEAR",
    "EXPECTED_SERVICE_DATE",
    "N_VISIT_DATE",
    "REG_NO"
        ]].copy() 
    customers_df = customers_df.rename(columns={"LAST_INTERACTION": "last_interaction_months"})
    customers = customers_df.to_dict(orient='records')
    if platform == "personalized_pitch":
        pitches_data_list = load_pitches_from_json("reminder_pitches_30s_2mins_all_languages.json")

        for customer in customers:
            #pitch = get_pitch(pitches_data_list, customer["segment_name"], lang)
            pitch = get_pitch(pitches_data_list, customer["segment_name"], lang, duration)
            #pitch = all_pitches[customer["segment_name"]][lang]
            pitch_dict = { 
            'customer_name': customer['CUSTOMER_NAME'],
            'segment_name': customer['segment_name'],
            'model': customer['SALE_SERIES'],
            'vehicle_age': customer['VEHICLE_AGE_YEAR'],
            'last_service_date': customer['N_VISIT_DATE'],
            'last_interaction_months': customer['last_interaction_months'],
            'expected_service_date': customer['EXPECTED_SERVICE_DATE'],
            'registration_no': customer['REG_NO'],
            'pitch': pitch
            }
            print(pitch_dict)
            return jsonify(pitch_dict)
        
    

    
    endpoint = os.getenv("ENDPOINT_URL")
    deployment = os.getenv("DEPLOYMENT_NAME")
    subscription_key = os.getenv("AZURE_OPENAI_API_KEY")
    api_version="2025-01-01-preview"
    for customer in customers:
        pitch = generate_pitch(
            customer_name=customer["CUSTOMER_NAME"],
            customer_care_executive=customer["DEALER_NAME"],
            customer_segment=customer["segment_name"],
            remaining_amc_services=customer["REMAINING_AMC_SERVICES"],
            expected_service_type=customer["EXPECTED_SERVICE_TYPE"],
            last_interaction_months=customer["last_interaction_months"],
            sale_series=customer["SALE_SERIES"],
            customer_type=customer["CUSTOMER_TYPE"],
            endpoint=endpoint,
            deployment=deployment,
            subscription_key=subscription_key,
            api_version=api_version,
            lang=lang
        )
        print(f"\n--- Customer Care Executive: {customer['DEALER_NAME']}  Customer: {customer['CUSTOMER_NAME']} ({customer['segment_name']}) ---")
        print(f"Vehicle: {customer['SALE_SERIES']}, Last Interaction: {customer['last_interaction_months']} months ago, AMC: {customer['REMAINING_AMC_SERVICES']}, Expected: {customer['EXPECTED_SERVICE_TYPE']}")
        print(f"Pitch Points: {pitch}")
        print("----------------------------------------------------------------")

        
        
        pitch_dict = { 
            'customer_name': customer['CUSTOMER_NAME'],
            'segment_name': customer['segment_name'],
            'model': customer['SALE_SERIES'],
            'vehicle_age': customer['VEHICLE_AGE_YEAR'],
            'last_service_date': customer['N_VISIT_DATE'],
            'last_interaction_months': customer['last_interaction_months'],
            'expected_service_date': customer['EXPECTED_SERVICE_DATE'],
            'registration_no': customer['REG_NO'],
            'pitch': pitch
        }
        print(pitch_dict)
    return jsonify(pitch_dict)

if __name__ == '__main__':
    app.run()