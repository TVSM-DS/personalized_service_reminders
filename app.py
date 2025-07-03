print("Import libraries")
from flask import Flask, request, jsonify
import requests
import os, sys
import json
from pyspark.sql.functions import date_format,to_date, to_timestamp, col;


def generate_pitch(customer_name: str, customer_care_executive: str, customer_segment: str, remaining_amc_services: float,
                   expected_service_type: str, last_interaction_months: int,
                   sale_series: str, customer_type: str,
                   endpoint: str, deployment: str, subscription_key: str, api_version: str) -> str:
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
        "Provide the 5 points in a concise, bulleted list format, suitable for a phone call."
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
  

app = Flask('personalized_pitch')
@app.route('/', methods=['GET'])
def hello():
    return jsonify({"message": "Personalized service remainder running!"})
@app.route('/smr/segmentation/pitches', methods=['POST'])
def generate_personalized_pitches():
    pitch_dict = {}
    #pitch_dict = {'customer_name': 'SIDDAPPA', 'segment_name': 'free_service_maximisers', 'model': 'XL 100', 'vehicle_age': 5, 'last_service_date': '01 Mar, 2021', 'last_interaction_months': '51', 'expected_service_date': '13 Jul, 2025', 'registration_no': 'KA45EC0087', 'pitch': "- **Hi there! Just a quick reminder:** Your TVS vehicle is due for its service. Keeping it in top shape ensures smooth rides and safety. \n\n- **Let's make it easy for you:** We offer free pick-up and drop services, so you don't have to worry about bringing your vehicle to us. Just sit back and relax!\n\n- **Save on service costs:** Consider our AMC plans. They help reduce the overall cost of maintaining your vehicle and keep it running smoothly without breaking the bank.\n\n- **You're in good hands:** Our trained TVS technicians know your vehicle inside out and will take great care of it. You can trust them to do a great job!\n\n- **Quick and hassle-free:** Our service is fast, so you won't be without your vehicle for long. Book your appointment now and get back on the road in no time!"}
    data = request.json
    reg_no= data['reg_no']   
    df = spark.sql("""
    SELECT *
    FROM sandbox.map_t_srv_mrkt_smr_all_dealers_daily_digi_app_july_2025_version_6_cluster WHERE REG_NO = '{}' """.format(reg_no))
    endpoint = os.getenv("ENDPOINT_URL", "https://tvsmazoogiboaidev01-ds-cin-svcmatea.openai.azure.com/")
    deployment = os.getenv("DEPLOYMENT_NAME", "gpt-4o-2")
    subscription_key = os.getenv("AZURE_OPENAI_API_KEY", "D9WwHmUBkuymKMHeQQ4LdAIplbQLR0XlDsZmuQbtKAMTpu3IBkUNJQQJ99BAAC77bzfXJ3w3AAABACOGAtmH")
    api_version="2025-01-01-preview"
    customers_from_df = df.select(
    col("CUSTOMER_NAME"),
    col("DEALER_NAME"),
    col("segment_name"),
    col("REMAINING_AMC_SERVICES"),
    col("EXPECTED_SERVICE_TYPE"),
    col("LAST_INTERACTION").alias("last_interaction_months"), # Assuming LAST_INTERACTION is in months
    col("SALE_SERIES"),
    col("CUSTOMER_TYPE"),
    col("VEHICLE_AGE_YEAR"),
    col("EXPECTED_SERVICE_DATE"),
    col("N_VISIT_DATE"),
    col("REG_NO")
    ).collect()
    customers = [row.asDict() for row in customers_from_df]
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
            api_version=api_version
        )
        # Print the generated pitch, clearly indicating the customer and their segment
        print(f"\n--- Customer Care Executive: {customer['DEALER_NAME']}  Customer: {customer['CUSTOMER_NAME']} ({customer['segment_name']}) ---")
        print(f"Vehicle: {customer['SALE_SERIES']}, Last Interaction: {customer['last_interaction_months']} months ago, AMC: {customer['REMAINING_AMC_SERVICES']}, Expected: {customer['EXPECTED_SERVICE_TYPE']}")
        print(f"Pitch Points: {pitch}")
        print("----------------------------------------------------------------")
        pitch_dict['customer_name'] = customer['CUSTOMER_NAME']
        pitch_dict['segment_name'] = customer['segment_name']
        pitch_dict['model'] = customer['SALE_SERIES']
        pitch_dict['vehicle_age'] = customer['VEHICLE_AGE_YEAR']
        pitch_dict['last_service_date'] = customer['N_VISIT_DATE']
        pitch_dict['last_interaction_months'] = customer['last_interaction_months']
        pitch_dict['expected_service_date'] = customer['EXPECTED_SERVICE_DATE']
        pitch_dict['registration_no'] = customer['REG_NO']
        pitch_dict['pitch'] = pitch
    return jsonify(pitch_dict)

if __name__ == '__main__':
    #app.run()
    app.run(host='0.0.0.0', port=5000, debug=True)