#!/usr/bin/python
import json

debug=0
zmqPort = 5556
zmqGPSPort = 5557

socketsPort = 9999
httpPort= 5000

serialPortName='/tmp/cronostamperCOM'

def mogrify(topic, msg):
    """ json encode the message and prepend the topic """
    return topic + ' ' + json.dumps(msg)

def demogrify(topicmsg):
    """ Inverse of mogrify() """
    json0 = topicmsg.find('{')
    topic = topicmsg[0:json0].strip()
    msg = json.loads(topicmsg[json0:])
    return topic, msg 
