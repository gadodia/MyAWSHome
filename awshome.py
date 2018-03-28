#!/usr/bin/env python

import os
import json
import time
import pi_switch
import sys
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient

class OnOff:
    def __init__(self, name, onCode, offCode, rf, iot):
        self.name = name
        self.onCode = onCode
        self.offCode = offCode
        self.rf = rf

        self.shadow = iot.createShadowHandlerWithName(self.name, True)
        self.shadow.shadowRegisterDeltaCallback(self.newShadow)
        self.set(False)

    # def set(self, state):
    #     code = self.onCode if state else self.offCode
    #     print('Turning %s %s using code %i' % (self.name, 'ON' if state else 'OFF', code))
    #     self.rf.sendDecimal(code, 24)
    #     self.shadow.shadowUpdate(json.dumps({
    #         'state': {
    #             'reported': {
    #                 'light': state
    #                 }
    #             }
    #         }
    #     ), None, 5)

    def set(self, state):
        code = self.onCode if state else self.offCode
        
        if self.name == 'all-lamps':
            if state:
                for code in (4218115, 4224259):
                    print('Turning %s %s using code %i' % (self.name, 'ON' if state else 'OFF', code))
                    self.rf.sendDecimal(code, 24)
                    time.sleep(0.2)
            else:
                for code in (4218124, 4224268):
                    print('Turning %s %s using code %i' % (self.name, 'ON' if state else 'OFF', code))
                    self.rf.sendDecimal(code, 24)
                    time.sleep(0.2)
        else:
            print('Turning %s %s using code %i' % (self.name, 'ON' if state else 'OFF', code))
            self.rf.sendDecimal(code, 24)

        self.shadow.shadowUpdate(json.dumps({
            'state': {
                'reported': {
                    'light': state
                    }
                }
            }
        ), None, 5)

    def newShadow(self, payload, responseStatus, token):
        newState = json.loads(payload)['state']['light']
        self.set(newState)

def createIoT():
    iot = AWSIoTMQTTShadowClient('AWSHome', useWebsocket=True)
    iot.configureEndpoint('**********.iot.us-east-1.amazonaws.com', 443)
    iot.configureCredentials(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'VeriSign-Class 3-Public-Primary-Certification-Authority-G5.pem'))
    iot.configureConnectDisconnectTimeout(10)  # 10 sec
    iot.configureMQTTOperationTimeout(5)  # 5 sec
    iot.connect()
    return iot

def createRF():
    rf = pi_switch.RCSwitchSender()
    rf.enableTransmit(0)
    rf.setPulseLength(194)
    return rf

if __name__ == "__main__":
    iot = createIoT()
    rf = createRF()

    # Create your switches here, using the format:
    #   OnOff(<THING NAME>, <ON CODE>, <OFF CODE>, rf, iot)
    #
    # Example:
    #   OnOff('floor-lamp', 284099, 284108, rf, iot)
    #
    OnOff('sleeping-lamp', 4218115, 4218124, rf, iot)
    OnOff('living-lamp',4224259 ,4224268 , rf, iot)
    OnOff('all-lamps',4224259 ,4224268 , rf, iot)

    
    print('Listening...')

    while True:
        time.sleep(0.2)
