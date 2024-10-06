import json
import logging

logger = logging.getLogger(__name__)

def classify_message(response_json):
    """
    Classify the message based on the response JSON.
    Returns a tuple of (classification, template_name, additional_function)
    """
    action = response_json.get('screen_0_Dropdown_0', '')
    
    classification_map = {
        "Escalation": ("Escalation", "hoa_escalation_m", None),
        "Connect Unit": ("Connect Unit", "connect_units_hoa_m", None),
        "Report Infrastructure Issue": ("Infrastructure Issue", "infrastructure_hoa_menu", None),
        "Update Address": ("Update Address", "update_address_menu", None),
        "Share Connect App": ("Share Connect App", "interest_register_menu", None),
        "Bulk Outage": ("Bulk Outage", "hoa_bulk_outage", "perform_hoa_test"),
    }
    
    if action in classification_map:
        return classification_map[action]
    elif 'screen_0_TextInput_1' in response_json:
        gated_id = response_json.get('screen_0_TextInput_1', '')
        return f"Outage Report - Gated ID: {gated_id}", None, None
    else:
        return "Unclassified", None, None


def process_interactive_message(message_data):
    """Process interactive message data."""
    interactive_data = message_data['interactive_data']
    if interactive_data['type'] == 'nfm_reply':
        nfm_reply = interactive_data['nfm_reply']
        try:
            response_json = json.loads(nfm_reply['response_json'])
            
            classification, template_name, additional_function = classify_message(response_json)
            logger.info(f"Message Classification: {classification}")

            # Instead of sending a template, we'll log the classification and template name
            if template_name:
                logger.info(f"Would have sent template: {template_name}")
            else:
                logger.info("No specific template for this classification")

            if additional_function == "perform_hoa_test":
                gated_id = response_json.get('screen_0_TextInput_1', '')

        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON in nfm_reply: {e}")
    else:
        logger.info(f"Unhandled interactive message type: {interactive_data['type']}")# You can add more classification-related functions here if needed
        

def extract_message_data(webhook_data):
    """
    Extract relevant data from the webhook message.
    Returns a tuple of (screen_0_Dropdown_0, screen_0_TextInput_1, full_response_json)
    """
    try:
        # Extract the message from the webhook data
        message = webhook_data['entry'][0]['changes'][0]['value']['messages'][0]
        
        # Check if it's an interactive message
        if message['type'] == 'interactive' and message['interactive']['type'] == 'nfm_reply':
            response_json_str = message['interactive']['nfm_reply']['response_json']
            response_json = json.loads(response_json_str)
            
            screen_0_Dropdown_0 = response_json.get('screen_0_Dropdown_0', '')
            screen_0_TextInput_1 = response_json.get('screen_0_TextInput_1', '')
            
            return (screen_0_Dropdown_0, screen_0_TextInput_1, response_json)
        else:
            return (None, None, None)
    
    except (KeyError, json.JSONDecodeError) as e:
        print(f"Error extracting data: {str(e)}")
        return (None, None, None)

# Example usage
webhook_message = {'object': 'whatsapp_business_account', 'entry': [{'id': '423282287532656', 'changes': [{'value': {'messaging_product': 'whatsapp', 'metadata': {'display_phone_number': '27691440799', 'phone_number_id': '343358652204774'}, 'contacts': [{'profile': {'name': 'Jay You Be Eye'}, 'wa_id': '27681161497'}], 'messages': [{'context': {'from': '27691440799', 'id': 'wamid.HBgLMjc2ODExNjE0OTcVAgARGBI5MTE3NzJCOUU1QUI0RTdFNUQA'}, 'from': '27681161497', 'id': 'wamid.HBgLMjc2ODExNjE0OTcVAgASGCA2NzM2RjEzMzg5OTQyQjA0QUZDMDA1MjhFOUYzMDdCOQA=', 'timestamp': '1727691590', 'type': 'interactive', 'interactive': {'type': 'nfm_reply', 'nfm_reply': {'response_json': '{"screen_0_Dropdown_0":"1_Full_Outage","screen_0_TextInput_1":"105","flow_token":"unused"}', 'body': 'Sent', 'name': 'flow'}}}]}, 'field': 'messages'}]}]}

dropdown_value, text_input_value, full_response = extract_message_data(webhook_message)

print(f"screen_0_Dropdown_0: {dropdown_value}")
print(f"screen_0_TextInput_1: {text_input_value}")
print(f"Full response JSON: {full_response}")