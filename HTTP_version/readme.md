RaspberryPi home automation

Pilot aspire to become a full home automation system and is based on RaspberryPi running Raspbian and a range of sensors and actuators. On this page I'll post the software running on the various nodes of the system, so far the following modules are available:

esp_pilot.ino - code running on ESP8266 modules and post data on apache server running on Raspberry
add.php - receive and process data sent by ESP nodes
mqtt_pilot.py - publish sensors feeds to Adafruit.io for remote visualization - https://io.adafruit.com/sebathorus/pilot-dashboard#
node_config.txt - contains pairing between nodes MAC addresses and AdafruitIO MQTT feed names
5c%3Acf%3A7f%3A82%3A47%3Abb_temphist.txt - is a sample of temperature log file generated by add.php script. It's format may change over time accordingly to project needs.