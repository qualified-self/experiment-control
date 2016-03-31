#!/bin/python
"""
HCI packet structure (6 bytes)
8 bit = C
8 bit = Command Type
8 bit = Dest ID
8 bit = Command
8 bit = arg1
8 bit = arg2

|| MAC_CMD_POWER | 0x81 | 0x01 ||
|| MAC_CMD_SD_STORAGE | 0x8D ||
|| MAC_CMD_SD_START | 0xA3 ||
|| MAC_CMD_SD_STOP | 0xA4 ||
|| MAC_CMD_RF_START | 0xA5 ||
|| MAC_CMD_RF_STOP | 0xA6 ||
|| MAC_CMD_START_DAQ | 0x82 ||
|| MAC_CMD_STOP_DAQ | 0x83 ||
|| MAC_CMD_QRS_START | 0xA7 ||
|| MAC_CMD_QRS_STOP | 0xA8 ||
|| MAC_CMD_SESSIONID | 0xA9 ||
|| MAC_CMD_GET_GROUPS | 0xAB ||
|| MAC_CMD_SET_GROUPS | 0xAA | Groups to join ||
|| MAC_CMD_DATE_ZERO | 0x8F | Minutes Seconds ||
|| MAC_CMD_DATE_ONE | 0x15 | Day Hours ||
|| MAC_CMD_DATE_TWO | 0x95 | Year Month ||
|| MAC_CMD_GET_DATE | 0xAC ||
|| CONFIG_NODE_ID | 0xB7 | New node ID ||
|| CONFIG_RF_CHANNEL | 0xB9 | New radiochannel ||
|| MAC_CMD_DISTRIBUTED_TIMESTAMP | 0xB2 ||
|| STORE_CONFIG | 0xB4 ||
|| MAC_CMD_GET_SERIAL | 0xB6 ||
|| GET_CONFIG | 0xB5 ||
"""
import struct
import logging

class CommandType:
	Group = "G"
	Node  = "N"
	Ext   = "E"

class Command:
	Power             = 0x81
	StorageOnly       = 0x8D
	StartStorage      = 0xA3
	StopStorage       = 0xA4
	StartRadio        = 0xA5
	StopRadio         = 0xA6
	StartAcquisition  = 0x82
	StopAcquisition   = 0x83
	StartQRSDetection = 0xA7
	StopQRSDetection  = 0xA8
	GetConfig         = 0xB5


class HCICommand:
	def __init__(self):
		pass

	def build_command(self, cmdtype, dest, cmd, arg1=0, arg2=0):
		sc = struct.pack("<ccBBBB", "C", cmdtype, dest, cmd, arg1, arg2)
		logging.info( ">>> CMD: {0}".format(sc) )
		return sc


def main():
	c = HCICommand()
	c.build_command(CommandType.Group, 0x01, Command.StartStorage)
	c.build_command(CommandType.Group, 0x01, Command.StopStorage)
	c.build_command(CommandType.Node,  0x01, Command.StartAcquisition)
	c.build_command(CommandType.Node,  0x01, Command.StopAcquisition)
	c.build_command(CommandType.Group, 0x01, Command.GetConfig)

if __name__ == "__main__":
	logging.basicConfig(level=logging.DEBUG)
	main()
