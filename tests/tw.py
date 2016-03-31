#!/usr/bin/env python
# -*- coding: utf8 -*-
import sys, os
import json
import optparse
import time
import logging
import subprocess

from twisted.internet import reactor, protocol
from txosc import osc
from txosc import dispatch
from txosc import async


# ###########################################################################
class UDPDispatcher(object):
    def __init__(self, port, host="127.0.0.1"):
        self.port = port
        self.host = host
        self.client = async.DatagramClientProtocol()
        self._client_port = reactor.listenUDP(0, self.client)

    def send(self, element):
        self.client.send(element, (self.host, self.port))
        print("Sent %s to %s:%d" % (element, self.host, self.port))
        
    # def send_messages(self):
    #     self._send(osc.Message("/ping"))
    #     self._send(osc.Message("/foo"))
    #     self._send(osc.Message("/ham/egg"))#, 3.14159))
    #     self._send(osc.Message("/spam", "hello", 1))
    #     self._send(osc.Message("/bacon", osc.TimeTagArgument()))
    #     self._send(osc.Message("/cheese"))
    #     self._send(osc.Message("/cheese/cheddar"))
    #     # of course, the /quit message has to be sent last!
    #     self._send(osc.Message("/quit"))
    #     print("Goodbye.")

class TMSTalk(protocol.Protocol):
    """Once connected, send a message, then print the result."""
    
    def connectionMade(self):
        #self.transport.write("hello, world!")
        print "protocol - connection made", 
    
    def dataReceived(self, data):
    	# @TODO parse incoming, put out as OSC for MAX
        print "protocol - server said:", data
        ##self.transport.loseConnection()
    
    def connectionLost(self, reason):
        print "protocol - connection lost"

class TMSTalkFactory(protocol.ClientFactory):
    protocol = TMSTalk

    def clientConnectionFailed(self, connector, reason):
		print "factory - connection failed"

    def clientConnectionLost(self, connector, reason):
		print "factory - connection lost"


# ###########################################################################
# M A I N
# ###########################################################################
if __name__ == '__main__':
	main()
