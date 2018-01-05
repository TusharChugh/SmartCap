"""
Code modified from the sample code of alexa skills kit-lambda function integration
"""
#Header files
from __future__ import print_function
import boto3
import json
import decimal
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
import calendar
import datetime

#Specify the dynamodb details
dynamodb = boto3.resource("dynamodb", region_name='us-east-1', endpoint_url="https://dynamodb.us-east-1.amazonaws.com")

table = dynamodb.Table('smartcap')

#TODO: Replace the app_id in the code

#Gets the data from dynamodb based on userid
def GetData(session):
    #timestamp = datetime.datetime.utcnow() - datetime.timedelta(minutes = 5)
    #days = (now - datetime.datetime(2016, 1, 1)).days 
    userId = session['user']['userId'].split('.') 
    userId = userId[3]
    try:
        response = table.query(
            KeyConditionExpression= Key('guid').eq(str(userId))
        )

        #print ("Got data: " + str(len(response)))
        print (response)
        for item in response['Items']:
            final_response = item["command"]
            tstamp = item["tstamp"]
        
        if (response['Count'] == 0):
            final_response = "No Data with this userid. You can ask to get the userid"
        
        else:
            now = datetime.datetime.utcnow()
            timestamp = int(round((now - datetime.datetime(2016, 1, 1)).total_seconds()))
            if ((timestamp - int(tstamp)) > 60):
                final_response = "No Data received from device in past 1 minute"
            
        return final_response
    except ClientError as e:
        print(e.response['Error']['Message'])


#The function is triggered by Alexa skills kit
def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    # print("event.session.application.applicationId=" +
    #       event['session']['application']['applicationId'])
          
    # print("event.session.application.userId=" +
    #       event['session']['application']['userId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    if (event['session']['application']['applicationId'] !=
            "amzn1.echo-sdk-ams.app.xxxx.xxxx"):
        raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "SceneDescription":
        return SceneDescriptionHandler(intent, session)
    # elif intent_name == "Describe":
    #     return DescribeHandler(intent, session)
    elif intent_name == "GetUserId":
        return GetUserIdHandler(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_help_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here

# --------------- Functions that control the skill's behavior ------------------


def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Sure. You can ask me to describe the scene "
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "You can ask me to describe the scene "
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, speech_output, reprompt_text, should_end_session))
        
def get_help_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Help"
    speech_output = "Smart Cap is an assistant for visually impaired which narrates"\
    "the description of scene by taking pictures from webcam. " \
    "It requires raspberry pi and a camera. Instructions to setup are on the github page. " \
    "If you have done the setup then first get your user info by saying. "\
    "Get my user info. "\
    "If you already have your user info setup then try saying. "\
    "Describe the scene. . . . "\
    "What command you want to try now?"\
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "You can ask me to describe the scene "
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying the Smart Cap " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, speech_output, None, should_end_session))


def SceneDescriptionHandler(intent, session):

    card_title = "Scene Description: "
    session_attributes = {}
    should_end_session = True
    data = GetData(session)
    print (str(data))
    speech_output = str(data)

    if 'Direction' in intent['slots'] and 'value' in intent['slots']['Direction']:
        direction = intent['slots']['Direction']['value']
        session_attributes = create_description_scene_attributes(direction)
        reprompt_text = "You can ask me to tell what is there in front of me "
        
    elif 'Environment' in intent['slots'] and 'value' in intent['slots']['Environment']:
        environment = intent['slots']['Environment']['value']
        session_attributes = create_description_scene_attributes(environment)
        reprompt_text = "You can ask me to describe the scene "
        
    elif 'Proximity' in intent['slots'] and 'value' in intent['slots']['Proximity']:
        proximity = intent['slots']['Proximity']['value']
        session_attributes = create_description_scene_attributes(proximity)
        reprompt_text = "You can ask me to descibe what is nearby "
        
    else:
        speech_output = "You can ask me to describe the scene "
        reprompt_text = "You can ask me to describe the scene " 
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, speech_output, reprompt_text, should_end_session))
        
def GetUserIdHandler(intent, session):

    card_title = "UserId"
    session_attributes = {}
    should_end_session = True

    if 'userid' in intent['slots']:
        userid = intent['slots']['userid']['value']
        session_attributes = create_description_scene_attributes(userid)
        data = session['user']['userId'].split('.') 
        print (str(data[3]))
        text_output = str(data[3])
        speech_output = "Your user info would now be visible on the card when" \
         " you login to Alexa app at alexa.amazon.com"
        reprompt_text = "You can ask me to get the user info " 
    else:
        speech_output = "You can ask me to get the user info "
        reprompt_text = "You can ask me to get the user info " 
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, text_output, reprompt_text, should_end_session))


def create_description_scene_attributes(description):
    return {"SceneDescription": description}


# def DescribeHandler(intent, session):
#     card_title = "Describe the scene"
#     session_attributes = {}
#     should_end_session = True

#     if 'Environment' in intent['slots']:
#         environment = intent['slots']['Environment']['value']
#         session_attributes = create_description_scene_attributes(environment)
#         data = GetData(session)
#         print (str(data))
#         speech_output = str(data)
#         reprompt_text = "You can ask me to describe the scene "
#     else:
#         speech_output = "You can ask me to describe the scene "
#         reprompt_text = "You can ask me to describe the scene "
#     return build_response(session_attributes, build_speechlet_response(
#         card_title, speech_output, reprompt_text, should_end_session))

# --------------- Helpers that build all of the responses ----------------------


def build_speechlet_response(title, output_speech, output_text, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output_speech
        },
        'card': {
            'type': 'Simple',
            'title': 'Smart Cap- ' + title,
            'content': 'Scene Description - ' + output_text
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }
