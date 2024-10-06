import logging
import re
from dotenv import load_dotenv
from flask import Flask, json, request, jsonify, session
from typing import Dict, Any
import requests
import os
from pymongo import MongoClient
from message_classifier import classify_message
import base64
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Retrieve environment variables
WEBHOOK_VERIFY_TOKEN = os.getenv('WEBHOOK_VERIFY_TOKEN')
print("WEBHOOK_VERIFY_TOKEN:", WEBHOOK_VERIFY_TOKEN)
GRAPH_API_TOKEN = os.getenv('GRAPH_API_TOKEN')
print("GRAPH_API_TOKEN:", GRAPH_API_TOKEN)
PORT = int(os.getenv('PORT', 3000))
print("PORT:", PORT)

MONGO_URI = os.getenv('MONGO_URI')  # Retrieve MongoDB URI from .env
MONGO_URI="mongodb+srv://maabanejubilant6:tbtQCFdA3dB4NHQI@backenddb.dorynel.mongodb.net"
print("MONGO_URI:", MONGO_URI)


# Set environment variables
HOA_MAIN_WELCOME_IMAGE_URL = os.getenv('HOA_MAIN_WELCOME_IMAGE_URL')
OPENSERVE_CONNECT_IMAGE_URL = os.getenv('OPENSERVE_CONNECT_IMAGE_URL')
OPENSERVE_HOA_BULK_OUTAGE_IMAGE_URL=os.getenv('OPENSERVE_HOA_BULK_OUTAGE_IMAGE_URL')
# Load environment variables
DATABASE_API_URL = os.getenv('DATABASE_API_URL', 'https://supabasefastapidev.azurewebsites.net/gated_communities/hoa_details')
URL_DATA_INSERT = os.getenv('URL_DATA_INSERT', 'https://supabasefastapidev.azurewebsites.net/webhook_data_inert')
BASE_URL=os.getenv('BASE_URL', 'https://supabasefastapidev.azurewebsites.net')
BUSINESS_PHONE_NUMBER_ID = os.getenv('BUSINESS_PHONE_NUMBER_ID')


print(HOA_MAIN_WELCOME_IMAGE_URL)
print(OPENSERVE_CONNECT_IMAGE_URL)
print(OPENSERVE_HOA_BULK_OUTAGE_IMAGE_URL)
print(DATABASE_API_URL)
print(URL_DATA_INSERT)

# Set up MongoDB client
client = MongoClient(MONGO_URI)
db = client['messages_sent']  # Replace with your actual database name
collection = db['messages_collection']  # Use your desired collection name


def send_message(phone_number_id, recipient, message_content, message_type="text", template_name="", language_code="en_US", parameters=["param1", "param2"]):
    url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
    
    headers = {
        "Authorization": f"Bearer {GRAPH_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Log the incoming request data
    logger.info(f"Incoming request data: phone_number_id={phone_number_id}, recipient={recipient}, "
                f"message_type={message_type}, template_name={template_name}, language_code={language_code}")

    # Log and print the incoming request data
    print("Incoming request data:")
    print(f"phone_number_id: {phone_number_id}")
    print(f"recipient: {recipient}")
    print(f"message_content: {message_content}")
    print(f"message_type: {message_type}")
    print(f"template_name: {template_name}")
    print(f"language_code: {language_code}")
    print(f"parameters: {parameters}")

    if message_type == "text":
        message_data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {
                "body": message_content
            }
        }
        
    
    elif message_type == "template":
        if template_name == "hoa_main_welcome_m_m":
            message_data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": recipient,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {
                        "code": language_code
                    },
                    "components": [
                        {
                            "type": "header",
                            "parameters": [
                                {
                                    "type": "image",
                                    "image": {
                                        "link": HOA_MAIN_WELCOME_IMAGE_URL
                                    }
                                }
                            ]
                        },
                        {
                            "type": "button",
                            "sub_type": "flow",
                            "index": 0
                        }
                    ]
                }
            }
        elif template_name == "interest_register_menu":
            message_data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": recipient,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {
                        "code": language_code
                    },
                    "components": [
                        {
                            "type": "header",
                            "parameters": [
                                {
                                    "type": "image",
                                    "image": {
                                        "link": OPENSERVE_CONNECT_IMAGE_URL
                                    }
                                }
                            ]
                        }
                    ]
                }
            }
        
        elif template_name == "hoa_bulk_outage2":
            message_data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": recipient,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {
                        "code": language_code
                    },
                    "components": [
                        {
                            "type": "header",
                            "parameters": [
                                {
                                    "type": "image",
                                    "image": {
                                        "link": OPENSERVE_HOA_BULK_OUTAGE_IMAGE_URL
                                    }
                                }
                            ]
                        },
                        {
                            "type": "button",
                            "sub_type": "flow",
                            "index": 0
                        }
                    ]
                }
            }
            
            try:
                perform_hoa_test(phone_number_id=phone_number_id, recipient=recipient)
            except Exception as e:
                logger.error(f"Error in perform_hoa_test: {str(e)}")
                
        elif template_name in ["hoa_escalation_m", "update_address_menu", "connect_units_hoa_m", "main_menu_hoa_m", "infrastructure_hoa_menu","hoa_area_outage"]:
            message_data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": recipient,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {
                        "code": language_code
                    },
                    "components": [
                        {
                            "type": "button",
                            "sub_type": "flow",
                            "index": 0
                        }
                    ]
                }
            }
        elif template_name in ["order_confirmation"]:
            message_data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": recipient,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {
                        "code": language_code
                    },
                    "components": [
                        {
                            "type": "body",
                            "parameters": [
                                {
                                    "type": "text",
                                    "text": parameters[0]
                                },
                                {
                                    "type": "text",
                                    "text": parameters[1]
                                }
                            ]
                        }
                    ]
                }
            }
        elif template_name in ["appointment_confirmation", "order_and_address_confirmation"]:
            message_data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": recipient,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {
                        "code": language_code
                    },
                    "components": [
                        {
                            "type": "body",
                            "parameters": [
                                {
                                    "type": "text",
                                    "text": parameters[0]
                                },
                                {
                                    "type": "text",
                                    "text": parameters[1]
                                }
                            ]
                        }
                    ]
                }
            }
        else:
            message_data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": recipient,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {
                        "code": language_code
                    }
                }
            }

    response = requests.post(url, headers=headers, json=message_data)
    return response.json(), response.status_code


def perform_hoa_test(phone_number_id=None, recipient=None):
    # Add your HOA test logic here
    logger.info("Performing HOA test for bulk outage scenario")
    # You can add more complex logic as needed
    # For example, you might want to query a database, update some records, etc.

def classify_message(response_json, raw_response,business_phone_number_id,user_phone_number):
    """
    Classify the message based on the response JSON.
    Returns the classification and response message.
    """
    base_url = BASE_URL
    database_api_endpoint = "/simplified_gated_community"
    #///Include timer to wait for 10 seconds before sending message///
    
    # Extract gated_id from response_json
    response_json_gated_id = response_json.get('screen_0_TextInput_1', '')
    logger.info("Extracted gated_id from response_json: %s", response_json_gated_id)
    
    # Extract gated_id from raw_response
    raw_response_gated_id = ''
    try:
        raw_response_data = json.loads(raw_response)
        if 'data' in raw_response_data and len(raw_response_data['data']) > 0:
            raw_response_gated_id = str(raw_response_data['data'][0].get('gated_id', ''))
        logger.info("Extracted gated_id from raw_response: %s", raw_response_gated_id)
    except json.JSONDecodeError:
        logger.error("Error: Unable to parse raw_response as JSON")

    # Compare gated_ids and choose the appropriate one
    if response_json_gated_id and raw_response_gated_id:
        if response_json_gated_id != raw_response_gated_id:
            gated_id = raw_response_gated_id
            logger.info("Gated IDs differ. Using gated_id from raw_response: %s", gated_id)
        else:
            gated_id = response_json_gated_id
            logger.info("Gated IDs are the same. Using gated_id: %s", gated_id)
    elif raw_response_gated_id:
        gated_id = raw_response_gated_id
        logger.info("Using gated_id from raw_response: %s", gated_id)
    else:
        gated_id = response_json_gated_id
        logger.info("Using gated_id from response_json: %s", gated_id)

    if not gated_id:
        logger.warning("No valid gated_id found in either response_json or raw_response")

    response_message = ""
    responded_to_client = False
    classification = 'Unknown'
    zone_test_result = None
    # Fetch gated community info if gated_id is available
    
    
    if gated_id:
        try:
            url = f"{base_url}{database_api_endpoint}?gated_id={gated_id}"
            logger.info("Fetching gated community info from URL: %s", url)
            response = requests.get(url)
            if response.status_code == 200:
                gated_info = response.json()
                
                # Log the preliminary information
                logger.info("Gated Community Info for ID %s:", gated_id)
                logger.info("Number of zones: %s", gated_info['number_of_zones'])
                logger.info("Zone Test Results:")
                
                all_zones_passed = True
                all_zones_failed = True
                for zone in gated_info['zones']:
                    logger.info("- %s: %s", zone['zone_name'], zone['test_result'])
                    if zone['test_result'].lower() != 'pass':
                        all_zones_passed = False
                    if zone['test_result'].lower() != 'fail':
                        all_zones_failed = False
                
                # Set the zone test result
                if all_zones_passed:
                    zone_test_result = "all_passed"
                elif all_zones_failed:
                    zone_test_result = "all_failed"
                else:
                    zone_test_result = "mixed"

                # Log additional community info
                raw_response_data = json.loads(raw_response)
                if 'data' in raw_response_data and len(raw_response_data['data']) > 0:
                    community_data = raw_response_data['data'][0]
                    logger.info("Additional Community Info:")
                    logger.info("Complex Name: %s", community_data['complex_name'])
                    logger.info("HOA Name: %s", community_data['hoa_name'])
                    logger.info("HOA Email: %s", community_data['hoa_email'])
                    logger.info("Phone Number: %s", community_data['phone_number'])
            else:
                response_message = f"Error fetching gated community info: Status code {response.status_code}"
                logger.error(response_message)
        except requests.RequestException as e:
            response_message = f"Error making API request: {e}"
            logger.error(response_message)
        except KeyError as e:
            response_message = f"Error parsing gated community info: {e}"
            logger.error(response_message)
    else:
        response_message = "No gated_id found in the provided data."
        logger.warning(response_message)


    # Classification logic
    if 'screen_0_TextInput_1' in response_json and response_json['screen_0_TextInput_1']:
        classification = 'TextInput'
    elif 'screen_0_TextArea_2' in response_json and response_json['screen_0_TextArea_2']:
        classification = 'TextArea'
    elif 'screen_0_Dropdown_0' in response_json and response_json['screen_0_Dropdown_0']:
        screen_0_Dropdown_0 = response_json['screen_0_Dropdown_0']
        if screen_0_Dropdown_0 == '1_Full_Outage':
            classification = 'Full Outage'
        elif screen_0_Dropdown_0 == '2_Partial_Outage':
            classification = 'Partial Outage'
        elif screen_0_Dropdown_0.startswith('0_'):
            classification = 'Dropdown Starting with 0'
        else:
            classification = 'Dropdown'
    else:
        classification = 'Unknown'
    
    logger.info("Classification: %s", classification)
    
    # Send message based on zone test result
    if zone_test_result == "all_passed":
        response_message = "Great news! All is well on our side. There are currently no detected outages affecting your area"
    elif zone_test_result == "all_failed":
        response_message = "It looks like you're estate is impacted by an outage. One of our technical support agents will be in contact with you."
        # send_email_to_backend(email_body, classification)
    elif zone_test_result == "mixed":
        response_message = "It looks like you're estate is impacted by an outage. One of our technical support agents will be in contact with you."
        
    else:
        response_message = ""

    logger.info("Response Message: %s", response_message)

    if response_message:
        logger.info("Final response message: %s", response_message)
        send_message(business_phone_number_id, user_phone_number, response_message)
        logger.info("Message sent directly to client: %s", response_message)
        return classification, response_message, True
    else:
        logger.info("No response message to send.")
        return classification, "", False

def get_image_data(image_id, business_phone_number_id):
    url = f"https://graph.facebook.com/v18.0/{image_id}"
    headers = {
        "Authorization": f"Bearer {GRAPH_API_TOKEN}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        image_url = response.json().get('url')
        if image_url:
            image_response = requests.get(image_url)
            if image_response.status_code == 200:
                return base64.b64encode(image_response.content).decode('utf-8')
    return None

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("Incoming webhook message:", data)
    
    changes = data.get('entry', [{}])[0].get('changes', [{}])[0].get('value', {})
    
    # Initialize variables
    responded_to_client = False
    business_phone_number_id = None
    user_phone_number = None
    
    # Mark message as read immediately
    if 'messages' in changes:
        message = changes['messages'][0]
        business_phone_number_id = changes.get('metadata', {}).get('phone_number_id')
        user_phone_number = message.get('from')
        
        if business_phone_number_id and 'id' in message:
            mark_message_as_read(business_phone_number_id, message['id'])
    
    database_api_url = DATABASE_API_URL
    url_data_insert = URL_DATA_INSERT
    INSERT_API_URL = url_data_insert
    
    # Create a session object
    session_requests = requests.Session()
    
    if 'messages' in changes:
        message = changes['messages'][0]
        print("Received message:", message)
        user_phone_number = message['from']
        print("User phone number:", user_phone_number)
        
        if message['type'] == 'text':
            business_phone_number_id = changes.get('metadata', {}).get('phone_number_id')
            print("Business phone number ID:", business_phone_number_id)
            user_message = message['text']['body'].lower()
            print("User message:", user_message)

            # Store values in the session
            session['user_phone_number'] = user_phone_number
            session['business_phone_number_id'] = business_phone_number_id

            # Check if phone number exists in the database
            try:
                db_response = session_requests.get(f"{database_api_url}?phone_number={user_phone_number}")
                raw_response = db_response.text  # Get raw response text
                print("Raw database response:", raw_response)
                
                if db_response.status_code == 404:
                    response_message = "You are not registered in our system. Please contact support for assistance."
                    send_message(business_phone_number_id, user_phone_number, response_message)
                    return jsonify(status="ok", message="User not registered"), 200
                    
                db_data = db_response.json()  # Parse response as JSON
                print("Parsed database response:", db_data)
                    
                if 'data' in db_data and isinstance(db_data['data'], list) and len(db_data['data']) > 0:
                    data_full = db_data['data'][0]
                    session['data'] = data_full
                    hoa_name = data_full.get('hoa_name', 'Guest')  # Default to 'Guest' if 'hoa_name' is not found
                    session['hoa_name'] = hoa_name
                    response_message = f"Welcome back {hoa_name}! How can we assist you today?"
                    print(f"business_phone_number_id: {business_phone_number_id}, user_phone_number: {user_phone_number}, response_message: {response_message}")
                else:
                    response_message = "Sorry, there was an issue processing your request. To return to the main menu, please type 'main menu' or say 'hello'."
                    send_message(business_phone_number_id, user_phone_number, response_message)
                    return jsonify(status="ok", message="Issue with request"), 200
                    
            except requests.RequestException as e:
                print(f"Error querying the database API: {e}")
                response_message = "There was an issue verifying your phone number. Please try again later."
                send_message(business_phone_number_id, user_phone_number, response_message)
                return jsonify(status="error", message="Database query failed"), 500
            
            template_name = ""
            response_message = ""
            
            # Check for integers in the message
            if re.search(r'\b\d+\b', user_message):
                print("Integer Triggered:", user_message)
                response_message = "Your request has been received and is being processed."
            
            elif "hello" in user_message or "hi" in user_message:
                template_name = "hoa_main_welcome_m_m"
            elif "main menu" in user_message or "menu" in user_message:
                template_name = "main_menu_hoa_m"
            elif "escalation" in user_message:
                template_name = "hoa_escalation_m"
            elif "report infrastructure issue" in user_message:
                template_name = "infrastructure_hoa_menu"
            elif "update address" in user_message:
                template_name = "update_address_menu"
            elif "interest_register" in user_message:
                template_name = "interest_register_menu"
            elif "Bulk Outage" in user_message:
                template_name = "hoa_bulk_outage2"
                additional_function = "perform_hoa_test"
            else:
                response_message = "Sorry, I did not understand your request."
            
            try:
                # Retrieve session data
                session_data = {
                    "hoa_name": session.get('hoa_name'),
                    "data": session.get('data')
                }
                print("Retrieved session data:", json.dumps(session_data, indent=2))

                if template_name:
                    send_message(business_phone_number_id, message['from'], "", "template", template_name)
                    return jsonify(status="ok", message="Template message sent successfully"), 200
                elif response_message:
                    print("About to send thank you message again")
                    send_message(business_phone_number_id, message['from'], response_message)
                    
                    return jsonify(status="ok", message="Response message sent successfully"), 200
                else:
                    return jsonify(status="error", message="No message to send"), 400

            except requests.RequestException as e:
                print(f"Error processing message: {e}")

        elif message['type'] == 'interactive':
            # Handle interactive response
            incoming_message = request.json
            try:
                user_response = incoming_message['messages'][0]
                print("Incoming for Email Trigger: ",incoming_message)
            except:
                user_response = None  # Handle the case where the key does not exist or another error occurs
            print("Incoming webhook message:", incoming_message)

            # Send data to the external API
            responseD = session_requests.post(INSERT_API_URL, json=incoming_message)
            if responseD.status_code == 200:
                print('Data successfully inserted into external API.')
            else:
                print('Failed to insert data into external API:', responseD.text)

            business_phone_number_id = None
            if 'entry' in incoming_message:
                entry = incoming_message['entry'][0]
                changes = entry.get('changes', [])
                if changes:
                    business_phone_number_id = changes[0]['value']['metadata'].get('phone_number_id')
            
            if not business_phone_number_id:
                return "Error: business_phone_number_id not found", 400
            
            interactive_response = message['interactive']
            response_json_str = interactive_response.get('nfm_reply', {}).get('response_json', '')
            response_json = interactive_response.get('nfm_reply', {}).get('response_json')

            response_json2 = json.loads(response_json_str)
            response_json_1ID = response_json2.get('screen_0_TextArea_1', '')
            screen_0_Dropdown_0 = response_json2.get('screen_0_Dropdown_0', '')
            print(screen_0_Dropdown_0)
            
            screen_0_TextInput_1 = response_json2.get('screen_0_TextInput_1', '')
            print(screen_0_TextInput_1)
            screen_0_TextArea_2 = response_json2.get('screen_0_TextArea_2', '')
            print(screen_0_TextArea_2)

            print("Interactive response JSON:", response_json2)
            print("response_json_1ID:", response_json_1ID)
            
            if response_json and isinstance(response_json, str):
                try:
                    response_json = json.loads(response_json)                             # Classify the message
                    
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")
                    return jsonify(status="error", message="Invalid JSON format"), 400
            else:
                print("Error: response_json is missing or not a string")
                return jsonify(status="error", message="Invalid response format"), 400
            
            def find_action_based_on_keywords(response_json, keywords):
                for key, value in response_json.items():
                    if isinstance(value, list):
                        match = next((item for item in value if isinstance(item, str) and any(keyword in item for keyword in keywords)), None)
                        if match:
                            return match
                    elif isinstance(value, str):
                        if any(keyword in value for keyword in keywords):
                            return value
                return None

            keywords = [
                'Escalation', 'Infrastructure', 'Support', 'Inquiry', 'Share_Connect_App',
                'Connect_Unit', 'Update_Address', 'Report_Infrastructure', 'Connect',
                'Bulk_Outage', 'Outage_Report', 'Service_Down', 'Network_Issue'
            ]
            action = find_action_based_on_keywords(response_json, keywords)
            print("Action:", action)

            template_name = ""
            response_message = ""

            if action == "4_Escalation" or action == "6_Escalation":
                template_name = "hoa_escalation_m"
                session['menu_selection_action'] = action
            elif action == "1_Connect_Unit/s":
                template_name = "connect_units_hoa_m"
                session['menu_selection_action'] = action
            elif action == "2_Report_Infrastructure_Issue":
                template_name = "infrastructure_hoa_menu"
                session['menu_selection_action'] = action
            elif action == "3_Update_Address":
                template_name = "update_address_menu"
                session['menu_selection_action'] = action
            elif action == "0_Share_Connect_App":
                template_name = "interest_register_menu"
                session['menu_selection_action'] = action
            elif action == "5_Bulk_Outage":
                template_name = "hoa_bulk_outage2"
                session['menu_selection_action'] = action
                additional_function = "perform_hoa_test"
            elif response_json_1ID:
                print(response_json)
                response_message = "Your request has been received and is being processed."
                
            else:
                summary_lines = []
                for key, value in response_json.items():
                    if isinstance(value, list):
                        summary_lines.extend([f"{key}: {v}" for v in value])
                    elif isinstance(value, (str, int)):
                        summary_lines.append(f"{key}: {value}")
                print("Second response triggered")

                try:
                    db_response = session_requests.get(f"{database_api_url}?phone_number={user_phone_number}")
                    raw_response = db_response.text

                    if responded_to_client:
                        # The message has already been sent to the client, so we can end the processing here
                        return jsonify({"status": "success", "message": "Response sent directly to client"}), 200
                except requests.RequestException as e:
                    print(f"Error querying the database API: {e}")
                    response_message = "There was an issue verifying your phone number. Please try again later."
                    send_message(business_phone_number_id, user_phone_number, response_message)
                    return jsonify(status="error", message="Database query failed"), 500
            
                if db_response.status_code == 404:
                    response_message = "You are not registered in our system. Please contact support for assistance."
                    send_message(business_phone_number_id, user_phone_number, response_message)
                    return jsonify(status="ok", message="User not registered"), 200
                    
                db_data = db_response.json()
                print("Parsed database response:", db_data)
                    
                if 'data' in db_data and isinstance(db_data['data'], list) and len(db_data['data']) > 0:
                    classification, response_message, responded_to_client = classify_message(response_json2, raw_response, business_phone_number_id, user_phone_number)
                    print("Export Raw Response:", response_message)
                    print("Classification:", classification)
                    print("Responded to client:", responded_to_client)
                    data_full = db_data['data'][0]
                    hoa_name = data_full.get('hoa_name', 'Guest')
                    response_message = f"Welcome back {hoa_name}! How can we assist you today?"
                    session['data_full'] = data_full
                    session['hoa_name'] = hoa_name
                    if user_phone_number and business_phone_number_id:
                        response2 = "About to send email"
                        print(response2)
                        print(f"business_phone_number_id: {business_phone_number_id}, user_phone_number: {user_phone_number}, response_message: {response_message}")
                    else:
                        logging.warning("User phone number or business phone number ID is missing.")
                else:
                    response_message = "Sorry, there was an issue processing your request. To return to the main menu, please type 'main menu' or say 'hello'."
                    send_message(business_phone_number_id, user_phone_number, response_message)
                    return jsonify(status="ok", message="Issue with request"), 200

                response_message = "Thank you for your request. We have received your message and will get back to you shortly."
                if additional_function == "perform_hoa_test":
                    response_message = "If you would like to return to the main menu, please type 'main menu' or say 'hello"

            try:
                # Retrieve session data
                session_data = {
                    "data_full": session.get('data_full'),
                    "hoa_name": session.get('hoa_name')
                }
                print("Retrieved session data:", json.dumps(session_data, indent=2))
                logging.info("Retrieved session data: %s", json.dumps(session_data, indent=2))
                
                # Ensure responded_to_client has a default value
                responded_to_client = getattr(locals(), 'responded_to_client', False)

                # Check if we need to send a template message
                if template_name:
                    send_message(business_phone_number_id, message['from'], "", "template", template_name)
                    return jsonify(status="ok", message="Template message sent successfully"), 200
               
                # Check if we've already responded to the client
                elif responded_to_client:
                    return jsonify({"status": "success", "message": "Response already sent directly to client"}), 200
               
                # If we haven't responded and have a response message, send it
                elif response_message:
                    print("About to send response message")
                    send_message(business_phone_number_id, message['from'], response_message)
                    return jsonify(status="ok", message="Response message sent successfully"), 200
               
                # If we have no message to send, return an error
                else:
                    return jsonify(status="error", message="No message to send"), 400

                try:
                    email_body = f"data_full: {session_data['data_full']}\nUser Response: {response_json2}"
                    classification = classify_interactive_response(response_json)
                    send_email_to_backend(email_body, classification)                    
                except Exception as e:
                    print(f"Failed to send email: {e}")
                
            except requests.RequestException as e:
                print(f"Error processing interactive response: {e}")
    
        elif message['type'] == 'image':
            print("Received image message:", message)
            response_message = "Thank you for providing the image. We will process it accordingly."
            try:
                send_message(business_phone_number_id, message['from'], response_message)
                
                # Get image data
                image_id = message['image']['id']
                image_data = get_image_data(image_id, business_phone_number_id)
                
                if image_data:
                    # Prepare email body
                    email_body = f"""
                    Received image from WhatsApp:
                    Sender: {message['from']}
                    Image ID: {image_id}
                    
                    Image data (base64 encoded):
                    {image_data}
                    """
                    
                    # Send email
                    send_email_to_backend(email_body, "WhatsApp Image")
                else:
                    print("Failed to retrieve image data")
            except requests.RequestException as e:
                print(f"Error processing image message: {e}")
    
    elif 'statuses' in changes:
        status = changes['statuses'][0]
        status_id = status['id']
        status_type = status['status']

        if status_type == 'delivered':
            print(f"Message with ID {status_id} has been delivered.")
        elif status_type == 'read':
            print(f"Message with ID {status_id} has been read.")
    
    else:
        print("Received unknown message type.")
    
    return jsonify(status="ok"), 200

def mark_message_as_read(business_phone_number_id, message_id):
    url = f"https://graph.facebook.com/v18.0/{business_phone_number_id}/messages"
    headers = {"Authorization": f"Bearer {GRAPH_API_TOKEN}"}
    payload = {
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": message_id
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            print(f"Message {message_id} marked as read successfully")
        else:
            print(f"Failed to mark message as read. Status code: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error marking message as read: {e}")

@app.route("/sendmessage", methods=["POST"])
def handle_send_message():
    try:
        data = request.json
        
        phone_number_id = BUSINESS_PHONE_NUMBER_ID
        print("phone_number_id:", phone_number_id)
        
        recipient = data.get("recipient")
        print("recipient:", recipient)
        message_content = data.get("message_content")
        message_type = data.get("message_type", "text")
        template_name = data.get("template_name", "")
        language_code = data.get("language_code", "en_US")
        parameters = data.get("parameters", ["2024-09-04", "S02879"])

        response, status_code = send_message(
            phone_number_id=phone_number_id,
            recipient=recipient,
            message_content=message_content,
            message_type=message_type,
            template_name=template_name,
            language_code=language_code,
            parameters=parameters
        )

        # Ensure response is JSON serializable
        if isinstance(response, dict):
            response_data = response
        else:
            response_data = {"message": "Message sent successfully"}

        return jsonify({"status": "success", "response": response_data}), status_code

    except Exception as e:
        print(f"Error in handle_send_message: {str(e)}")  # Add this line for debugging
        return jsonify({"status": "error", "message": str(e)}), 500


def classify_interactive_response(response_json):
    # Example classification logic
    if 'screen_0_Dropdown_0' in response_json and 'Order/Fault' in response_json['screen_0_Dropdown_0']:
        classification = 'Order/Fault'
    else:
        classification = 'Unknown'
        logging.info(f"Full message: {response_json}")
        print(f"Full message: {response_json}")
    
    # Log or print the classification
    logging.info(f"Classification: {classification}")
    print(f"Classification: {classification}")
    
    # Log or print the entire message if it's an Order/Fault
    if classification == 'Order/Fault':
        logging.info(f"Full message: {response_json}")
        print(f"Full message: {response_json}")
    
    return classification


def send_email_to_backend(email_body, classification):
    if classification is None:
        print("Classification is None, not sending email.")
        return

    # Define a mapping of classifications to email addresses
    classification_email_map = {
        "Order/Fault": "maabanejubilant6@gmail.com",
        "Support": "support@example.com",
        "Inquiry": "inquiry@example.com",
        # Add more mappings as needed
    }

    # Get the email address based on the classification
    to_email = classification_email_map.get(classification, "maabanejubilant6@gmail.com")

    # API endpoint and payload
    logging.info(f"Email body: {email_body}")
    api_url = 'https://google-smtp-server-api-1.onrender.com/send-email'
    payload = {
        "to_email": to_email,
        "subject": f"Classification: {classification}",
        "body": f"Classification: {classification}\n\n{email_body}"
    }
    
    # Send the POST request
    response = requests.post(api_url, json=payload)
    
    # Check the response status
    if response.status_code == 200:
        print("Email sent successfully.")
    else:
        print(f"Failed to send email. Status code: {response.status_code}, Response: {response.text}")

@app.route("/getMessages", methods=["GET"])
def get_messages():
    try:
        # Extract query parameters to build the match condition dynamically
        match_conditions = {}
        recipient = request.args.get('recipient')
        status = request.args.get('status')  # Get status from query parameter

        # Add conditions only if they are provided in the query params
        if recipient:
            match_conditions['recipient'] = recipient
        if status:
            match_conditions['status_code'] = status  # Match the specific status

        # Print match conditions for debugging
        print("Match conditions:", match_conditions)

        # MongoDB aggregation pipeline with dynamic match conditions
        pipeline = [
            {
                '$match': match_conditions
            },
            {
                '$sort': {
                    '_id': -1  # Sort by most recent messages first
                }
            },
            {
                '$project': {
                    '_id': 0  # Exclude the MongoDB document ID if not needed
                }
            }
        ]

        # Retrieve and return the matched messages
        messages = list(collection.aggregate(pipeline))
        print("Messages found:", messages)  # Debugging
        return jsonify({"messages": messages}), 200
    
    except Exception as e:
        print("Error retrieving messages:", e)
        return jsonify({"error": "Failed to retrieve messages", "details": str(e)}), 500

@app.route("/status", methods=["GET"])
def status():
    return jsonify({"status": "Server is running"}), 200

@app.route("/webhook", methods=["GET"])
def webhook_verification():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    
    if mode and token:
        if mode == "subscribe" and token == WEBHOOK_VERIFY_TOKEN:
            print("Webhook verified.")
            return challenge, 200
        else:
            print("Webhook verification failed.")
            return "Forbidden", 403



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)