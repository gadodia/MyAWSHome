import logging
import boto3
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

client = boto3.client('iot-data')

def lambda_handler(event, context):
    logger.info('got event{}'.format(event))
    access_token = event['payload']['accessToken']
    if (event['header']['namespace'] == 'Alexa.ConnectedHome.Discovery' and
        event['header']['name'] == 'DiscoverAppliancesRequest'):
        return handleDiscovery(context, event)
    elif event['header']['namespace'] == 'Alexa.ConnectedHome.Control':
        return handleControl(context, event)

def handleDiscovery(context, event):
    return {
        'header': {
            'messageId': event['header']['messageId'],
            'name': 'DiscoverAppliancesResponse',
            'namespace': 'Alexa.ConnectedHome.Discovery',
            'payloadVersion': '2'
        },
        'payload': {
            'discoveredAppliances': [
                {
                    'applianceId': 'living-lamp',
                    'friendlyName': 'Living Lamp',
                    'friendlyDescription': 'The living lamp controlled by Raspberry Pi and RF switch 5',
                    'actions': [
                        'turnOn',
                        'turnOff'
                    ],
                    'additionalApplianceDetails': {},
                    'isReachable': True,
                    'manufacturerName': 'MyAwsHome',
                    'modelName': '1',
                    'version': '1'
                },
                {
                    'applianceId': 'sleeping-lamp',
                    'friendlyName': 'Sleeping Lamp',
                    'friendlyDescription': 'The sleeping lamp controlled by Raspberry Pi and RF switch 4',
                    'actions': [
                        'turnOn',
                        'turnOff'
                    ],
                    'additionalApplianceDetails': {},
                    'isReachable': True,
                    'manufacturerName': 'MyAwsHome',
                    'modelName': '1',
                    'version': '1'
                },
                {
                    'applianceId': 'all-lamps',
                    'friendlyName': 'All Lamps',
                    'friendlyDescription': 'All lamps controlled by Raspberry Pi and RF switch 4,5',
                    'actions': [
                        'turnOn',
                        'turnOff'
                    ],
                    'additionalApplianceDetails': {},
                    'isReachable': True,
                    'manufacturerName': 'MyAwsHome',
                    'modelName': '1',
                    'version': '1'
                }
            ]
        }
    }

def handleControl(context, event):
    device_id = event['payload']['appliance']['applianceId']
    requestType = event['header']['name']
    if requestType == 'TurnOnRequest':
        name = 'TurnOnConfirmation'
        light = True
    elif requestType == 'TurnOffRequest':
        name = 'TurnOffConfirmation'
        light = False
    # we don't support other requestTypes yet

    logger.info('turning %s %s' % ('on' if light else 'off', device_id))
    
    if device_id == 'all-lamps':
        for d_id in ('sleeping-lamp', 'living-lamp'):
            response = client.update_thing_shadow(
                thingName=d_id,
                payload=json.dumps({
                    'state': {
                        'desired': {
                            'light': light
                        }
                    }
                })
            )
            logger.info('received {}'.format(response))    
    else:
        response = client.update_thing_shadow(
            thingName=device_id,
            payload=json.dumps({
                'state': {
                    'desired': {
                        'light': light
                    }
                }
            })
        )

        logger.info('received {}'.format(response))

    return {
        'header': {
            "messageId": event['header']['messageId'],
            "name": name,
            "namespace":"Alexa.ConnectedHome.Control",
            "payloadVersion":"2"
        },
        'payload': {}
    }
