# Pilot
RaspberryPi home automation

Pilot aspire to become a full home automation system and is based on RaspberryPi running Raspbian Jessie(at the moment) and a range of sensors and actuators.
On this page I'll post the software running on the various nodes of the system.

Two versions are available:
- HTTP_version - this is an early version, data transfer between nodes and server is achieved with POST requests.
- MQTT - uses Mosquitto broker + Paho Python Client(Raspberry) + PubSub Client(ESP8266) + feeds for data exchange between nodes. This is the most recent version.
