On this page I'll post the software running on the various nodes of the system, so far the following modules are available:

esp_mqtt.ino - code running on ESP8266 modules - publish data to temperature, humidity, light and detection feeds, subscribe to commands feed.

ada_mqtt.py - publish sensors feeds to Adafruit.io for remote visualization - https://io.adafruit.com/sebathorus/pilot-dashboard#

pilot_mqtt.py - subscribe to sensors feed and save received data

node_config.txt - contains pairing between nodes MAC addresses and AdafruitIO MQTT feed names
