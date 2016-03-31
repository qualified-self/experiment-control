import time
import os
import threading
import logging
import optparse
import struct

try:
    # fail gently if the dependency is missing, explain where to get it
    import OSC
except ImportError:
    print("OSC module is required for interprocess communication. Please see: https://trac.v2.nl/wiki/pyOSC")


class HolstOSC( object ):
    def set_verbose( self, onoff ):
        self.verbose = onoff;


    def sendMessage( self, path, args ):
        msg = OSC.OSCMessage()
        msg.setAddress( path )
        for a in args:
            msg.append( a )
        try:
            self.host.send( msg )
            if self.verbose:
                print( "sending message", msg )
        except OSC.OSCClientError:
            if self.verbose:
                print( "error sending message", msg )

    def dataMessage( self, nodeid,  beaconseq, packetId, timeslotPacket, frameType, data ):
        alldata = [ nodeid, frameType, packetId, beaconseq, 0, timeslotPacket ]
        alldata.extend( data )
        self.sendMessage( "/holst/rawdata", alldata )
        if self.verbose:
            print( "sending osc message with data", nodeid, data )

    def eventMessage( self, nodeid, beaconseq, packetId, timeslotPacket, frameType, eventType, eventData ):
        if eventType == 0x10:
            alldata = [ nodeid, frameType, packetId, beaconseq, eventType, timeslotPacket, 0 ]
            b = ""
            for byte in eventData[0:8]:
                b = b + chr( byte )
            alldata.append( struct.unpack( '<d', b ) )
            self.sendMessage( "/holst/event", alldata )
        if self.verbose:
            print( "sending osc message with event data", nodeid, eventType, eventData )

    def __init__(self, hostip, hostport ): #, myip, myport, hive ):
        self.verbose = False
        self.hostport = hostport
        self.hostip = hostip

        self.host = OSC.OSCClient()
        send_address = ( self.hostip, self.hostport )
        self.host.connect( send_address )

    def set_serial( self, serial ):
        self.serial = serial


