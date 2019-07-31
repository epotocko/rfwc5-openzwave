#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Program the Cooper RFWC5 buttons to trigger scene activation commands using python-openzwave.
		:platform: Unix, Windows, MacOS X
License : GPL(v3)
"""

# Settings
DEVICE = "/dev/ttyUSB0"
HOME_ID = 0x12345678
CONTROLLER_NODE_ID = 0x01
SCENE_CONTROLLER_NODE_ID = 0x02 # Node ID of RFWC5
CONFIG_PATH = "/test/python-openzwave/openzwave/config"
LOG_FILE_PATH = "/test/OZW_Log.log"

import logging
import sys, os, time

logging.basicConfig(level = logging.INFO)

logger = logging.getLogger('openzwave')

import openzwave
from openzwave.node import ZWaveNode
from openzwave.value import ZWaveValue
from openzwave.scene import ZWaveScene
from openzwave.controller import ZWaveController
from openzwave.network import ZWaveNetwork
from openzwave.option import ZWaveOption
import inspect
import six
if six.PY3:
	from pydispatch import dispatcher
else:
	from louie import dispatcher

# Define some manager options
options = ZWaveOption(DEVICE, config_path = CONFIG_PATH, user_path = ".", cmd_line = "")
options.set_log_file(LOG_FILE_PATH)
options.set_append_log_file(True)
options.set_console_output(True)
options.set_save_log_level("Debug")
options.set_logging(True)
options.lock()

class ZWaveRawNode:
	def __init__(self, network, home_id, node_id, delay = 5.0):
		self.network = network
		self.home_id = home_id
		self.node_id = node_id
		self.delay = delay

	# Send raw data to a device
	def _send(self, command_class, command, data, loginfo = None):
		if loginfo is None:
			loginfo = inspect.currentframe().f_back.f_code.co_name
		header = [
			self.node_id,  # Destination node id
			len(data) + 2, # Length of data (add 2 for COMMAND_CLASS/COMMAND)			
			command_class, # COMMAND_CLASS
			command        # COMMAND
		]
		# REQUEST = 0x00 - https://github.com/OpenZWave/open-zwave/blob/master/cpp/src/Defs.h#L239
		self.network.manager.sendRawData(self.home_id, self.node_id, loginfo, 0x00, False, bytes(header + data))
		time.sleep(self.delay)

	# COMMAND_CLASS_ASSOCIATION / ASSOCIATION_SET
	def association_set(self, group_id, node_ids):
		return self._send(0x85, 0x01, [group_id] + node_ids)

	# COMMAND_CLASS_ASSOCIATION / ASSOCIATION_GET
	def association_get(self, group_id):
		return self._send(0x85, 0x02, [group_id])
	
	# COMMAND_CLASS_ASSOCIATION / ASSOCIATION_REMOVE
	def association_remove(self, group_id, node_ids):
		return self._send(0x85, 0x04, [group_id] + node_ids)
		
	# COMMAND_CLASS_CONFIGURATION / CONFIGURATION_SET
	def configuration_set(self, parameter_number, size, configuration_value):
		return self._send(0x70, 0x03, [parameter_number, size, configuration_value])
		
	# COMMAND_CLASS_SCENE_CONTROLLER_CONF / SCENE_CONTROLLER_CONF_SET
	def scene_controller_conf_set(self, group_id, scene_id, dimming_duration):
		return self._send(0x2d, 0x01, [group_id, scene_id, dimming_duration])
	
	# COMMAND_CLASS_SCENE_CONTROLLER_CONF / SCENE_CONTROLLER_CONF_GET
	def scene_controller_conf_get(self, group_id):
		return self._send(0x2d, 0x02, [group_id])

# Program a single button on the RFWC5
def program_button(node, controller_node_id, group_id, scene_id, dimming_duration, level = 0x32):
	node.association_remove(group_id, [])
	node.association_get(group_id)
	node.association_set(group_id, [controller_node_id])
	node.association_get(group_id)
	node.configuration_set(group_id, 1, level)
	node.scene_controller_conf_set(group_id, scene_id, dimming_duration)
	# Association is being reset after scene_controller_conf_set
	node.association_set(group_id, [controller_node_id])
	node.association_get(group_id)
	node.scene_controller_conf_get(group_id)

def louie_network_started(network):
	print("Hello from network : I'm started : homeid {:08x} - {} nodes were found.".format(network.home_id, network.nodes_count))

def louie_network_failed(network):
	print("Hello from network : can't load :(.")

def louie_network_ready(network):
	print("Hello from network : I'm ready : {} nodes were found.".format(network.nodes_count))
	print("Hello from network : my controller is : {}".format(network.controller))
	dispatcher.connect(louie_node_update, ZWaveNetwork.SIGNAL_NODE)
	dispatcher.connect(louie_value_update, ZWaveNetwork.SIGNAL_VALUE)

def louie_node_update(network, node):
	print("Hello from node : {}.".format(node))

def louie_value_update(network, node, value):
	print("Hello from value : {}.".format( value ))

# Create a network object
network = ZWaveNetwork(options, autostart = False)

# We connect to the louie dispatcher
dispatcher.connect(louie_network_started, ZWaveNetwork.SIGNAL_NETWORK_STARTED)
dispatcher.connect(louie_network_failed, ZWaveNetwork.SIGNAL_NETWORK_FAILED)
dispatcher.connect(louie_network_ready, ZWaveNetwork.SIGNAL_NETWORK_READY)

network.start()

# We wait for the network.
print("***** Waiting for network to become ready : ")
for i in range(0, 30):
	if network.state >= network.STATE_READY:
		print("***** Network is ready")
		break
	else:
		sys.stdout.write(".")
		sys.stdout.flush()
		time.sleep(1.0)

# Program the 5 buttons to trigger a scene with an id equal to the group id
node = ZWaveRawNode(network, HOME_ID, SCENE_CONTROLLER_NODE_ID)
for i in range(5):
	program_button(node, CONTROLLER_NODE_ID, i + 1, i + 1, 0x00)

time.sleep(20.0)

network.stop()
