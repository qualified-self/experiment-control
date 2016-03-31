#!/usr/bin/env python
# -*- coding: utf8 -*-
import sys, os
import json
import optparse
import time
import logging
import subprocess
import string

# libs developed at the Philips residence
from libnexus import *
from libholst import *

import OSC

from twisted.internet import reactor, protocol
from txosc import osc, dispatch, async

__author__ = "Luis Rodil-Fernandez <root@derfunke.net>"
__version__ = "0.9b"

CONFIG = None


OSCTX = None
dest_address = None

# ###########################################################################
# class UDPDispatcher(async.DatagramClientProtocol):
#     def __init__(self, port, host="127.0.0.1"):
#         self.port = port
#         self.host = host
#         self.client = async.DatagramClientProtocol()
#         self._client_port = reactor.listenUDP(0, self.client)

#     def send(self, element):
#         self.client.send(element, (self.host, self.port))
#         print("Sent %s to %s:%d" % (element, self.host, self.port))

#     # def send_messages(self):
#     #     self._send(osc.Message("/ping"))
#     #     self._send(osc.Message("/foo"))
#     #     self._send(osc.Message("/ham/egg"))#, 3.14159))
#     #     self._send(osc.Message("/spam", "hello", 1))
#     #     self._send(osc.Message("/bacon", osc.TimeTagArgument()))
#     #     self._send(osc.Message("/cheese"))
#     #     self._send(osc.Message("/cheese/cheddar"))
#     #     # of course, the /quit message has to be sent last!
#     #     self._send(osc.Message("/quit"))
#     #     print("Goodbye.")

import math

class MovingStats:
    def __init__(self, alphaOrN):
        self.mean = 0
        self.var = 0
        self.started = False
        if (alphaOrN > 1):
            self.alpha = 2 / (alphaOrN - 1)
        else:
            self.alpha = alphaOrN

    def update(self, value):
        if (not self.started):
            self.mean = value
            self.var = 0
            self.started = True
        else:
            self.mean = self.mean - self.alpha * (self.mean - value);
            diff = value - self.mean
            self.var  = self.var - self.alpha * (self.var  - diff*diff);

    def normalize(self, value):
        stddev = math.sqrt(self.var)
        return ( value - self.mean ) / (stddev + 1e-10)

    def normalize01(self, value):
        norm = self.normalize(value)
        norm = norm / 6.0 + 0.5
        return norm

ecgStats  = MovingStats(0.01)
respStats = MovingStats(0.01)

class TMSTalk(protocol.Protocol):
    """Protocol bridging implementation for the tmsi_server."""
    def __init__(self, addr):
        self.address = addr
        #self.osc = UDPDispatcher()

    def connectionMade(self):
        print "connection made on port ", self.address.port

    def dispatch( self, path, args ):
        global OSCTX
        msg = OSC.OSCMessage()
        msg.setAddress( path )
        for a in args:
            msg.append( a )
        try:
            print msg
            OSCTX.send( msg )
        except OSC.OSCClientError:
            print( "sending OSC failed", msg )

    def dataReceived(self, data):
        # @TODO parse incoming, put out as OSC for MAX
        if data:
            # sanitize incoming data
            clean = data.strip()
            clean = clean.replace("\"", "")
            #print clean
            oscaddress = "/sensorbox/{0}".format(self.address.port)
            # create params list
            tmp = clean.split()

            currentBox = None
            for box in CONFIG['boxes']:
                if (int(self.address.port) == int(box['port'])):
                    currentBox = box
                    break
            if (currentBox == None):
                print "Error: unknown box: " + str(self.address.port)

            nChannels = len(currentBox['channels'])+1
            #params.append( float(tmp[1].strip()) )
            #params.append( float(tmp[2]) )
            #params.append( float(tmp[3]) )
            # #print tmp[1:]
            nMessages = int(len(tmp) / nChannels)
            for n in range(nMessages):
                params = []
                subtmp = tmp[n*nChannels:(n+1)*nChannels]
                ecg = float(subtmp[1])
                resp = float(subtmp[2])
                ecgStats.update(ecg)
                respStats.update(resp)
                subtmp[1] = ecgStats.normalize01(ecg)
                subtmp[2] = respStats.normalize01(resp)
                for p in subtmp:
                    params.append(float(p))
                self.dispatch(oscaddress, params)

        #data = string.trim(data)
        #params = data.split()
        #msg = osc.Message("/sensorbox", self.address._client_port, *params)
        #self.osc.send( msg )

    def connectionLost(self, reason):
        print "connection lost on port {0}".format(self.address.port)

class TMSTalkFactory(protocol.ClientFactory):
    #protocol = TMSTalk
    def buildProtocol(self, addr):
        print "factory - ", addr
        return TMSTalk(addr)

    def clientConnectionFailed(self, connector, reason):
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        reactor.stop()

# ###########################################################################
def main():
    global OSCTX, dest_address
    option_parser_class = optparse.OptionParser

    parser = option_parser_class(description='Run an ILINX experiment')

    parser.add_option('-v','--verbose',
        action='store_true',
        dest="verbose",
        default=False,
        help='verbose printing [default:%i]'% False)

    parser.add_option('-x','--experiment',
        action='store',
        type="string",
        dest="experiment",
        default="exp",
        help='name of experiment [default:%s]'% "")

    (options,args) = parser.parse_args()

    global CONFIG
    fcfg = 'experiment.json'
    print "Reading config from {0}".format(fcfg)
    with open(fcfg) as f:
        CONFIG = json.loads( f.read() )

    print
    print

    servers = []

    try:
        if CONFIG['are-hosts-remote'] == True:
            print "(!!!) Nexus hosts are remote. Will not spawn server processes."
        else:
            # start an instance of a nexus server for every box in the experiment
            for sensorbox in CONFIG['boxes']:
                nxs = NexusLauncher(options.experiment)
                nxs.launch( sensorbox )
                servers.append( nxs )

        OSCTX = OSC.OSCClient()
        dest_address = ( CONFIG['destination-host'], CONFIG['destination-port'] )
        print "connecting via OSC to {0}:{1}".format(dest_address[0], dest_address[1])
        OSCTX.connect( dest_address )

        # sleep for some time to give the OS some time to catch up
        time.sleep(5)

        # initialize client connections
        connections = []
        f = TMSTalkFactory()
        # start as many TMSTalk clients as we have servers
        for s in CONFIG['boxes']:
            conn = reactor.connectTCP(s['host'], int(s['port']), f)
            print "Starting {0} client, connecting to {1}:{2}".format(conn.getDestination().type, conn.getDestination().host, conn.getDestination().port)
            connections.append(conn)

        # start the twisted reactions that will start the async communication
        reactor.run()

        # print output while running
        # while True:
        #   for s in servers:
        #       s.printout()

    except KeyboardInterrupt, e:
        # @TODO send Ctrl-C to all subprocesses
        reactor.stop()
        for s in servers:
            s.terminate()
        print
        print "Seems that you want to exit. Goodbye!"
        pass


# ###########################################################################
# M A I N
# ###########################################################################
if __name__ == '__main__':
    main()
