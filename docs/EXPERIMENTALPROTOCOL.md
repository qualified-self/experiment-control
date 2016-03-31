# Experimental Protocol

Checklist for experimental protocol.

### Before start of experiment
  - Synchronize clocks of all measurement devices
  - Prep sensors and electrodes
  - (?) Baseline measurements to group inviduals with similar biometrics
  - If experiment takes place in an environment of deprivation, make sure there are no leaks (e.g. sound or light): 
       - in the ambient of the room 
       - or coming from the measurement devices themselves 
       - the system's equipment
  - Test the feedback system (e.g. make sure lights go brighter as you breath instead of dimmer)

### At start of experiment
  - Take note of date and time of day in logbook.
  - If Nexus is used: instruct participants to click on button at beginning of experiment to obtain mark in recording.
  - If HOLST necklace is used: restart the clocks in all nodes by resetting the base station.

### At end of experiment
  - If Nexus is used: instruct participants to click on button at beginning of experiment to obtain mark in recording.
  - If HOLST necklace is used: stop logging.
  - Interview (as per Chris' preferred ethnographic methodology which has proved very valuable for later analysis)

### After end of experiment
  - Gather data (comprising EDF files containing biometrics, video if any, audio if any, recording of interviews and logbook describing experiments and time marks)
  - Share data among all parties
  - Check-in code
  - Share time log
  - Stand-up meeting for brief data analysis and conclusion

## Feedback system

The feedback system is composed of the following parts.

### Measurement devices

#### Nexus
  - 1x Nexus 10 (must be a "BT always ON") per participant in experiment.
  - Channels:
	- "A" : "ECG"
	- "E" : "RESP"
	- "G" : "GSR"
	- "H" : "LIGHT"

#### HOLST
1x HOLST ECG necklace per participant
1x HOLST radio base station

### DAQ (data aquisition)

#### Nexus
tmsi_server by Ad Denissen.

#### HOLST
pyholstparser by Marije Baalman or libholst by Luis Rodil-Fernandez.

### Interfacing with stage systems
experiment.py by Luis Rodil-Fernandez (talks to tmsi_server and libholst)
MAX/MSP patches by Maurizio "TeZ" Martinucci

### Environmental actuators
Philips HUE (not enough resolution)
DMX wall washer
Many more to come
