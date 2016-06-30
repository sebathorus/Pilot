#include <ESP8266WiFi.h>
#include <OneWire.h>
#include <PubSubClient.h>

const char* ssid = "own_ssid"; // Your ssid
const char* password = "own_pass"; // Your Password
uint8_t mac[6];
String espMAC;
long lastMsg = 0;
char msg[50];
char espMAC2[12];
int value = 23;
char nodefeed[33];
byte i;
byte present = 0;
byte type_s;
byte data[12];
byte addr[8];
float celsius, fahrenheit;

WiFiClient espClient;
PubSubClient client(espClient);

const char* mqtt_server = "aaa.bbb.ccc.ddd";//IP of RaspberryPi broker

OneWire ds(2);  // on pin 2 a 4.7K resistor is required between DS18B20 data pin and Vcc
//WiFiServer server(80);

String macToStr(const uint8_t* mac)//convert MAC address to a String
{
  String result;
  for (int i = 0; i < 6; ++i) {
    result += String(mac[i], 16);
  }
  return result;
}

//this function process messages arrived on "sensorsfeed/commands/espMAC" feed, where espMAC is the actual MAC address of the node detected by code
void callback(char* topic, byte* payload, unsigned int mqttlength) {
  String recMAC;
  String recpayload;
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.println("] ");
  for (int i = 0; i < mqttlength; i++) {
    recpayload += (char)payload[i];
  }
  
  Serial.print("recpayload ");
  Serial.println(recpayload);
  
  if (recpayload == "1") {
      Serial.println("Turn LED ON");//if message payload is "1" this message is print on serial console
    } else {
    Serial.println("Turn LED Off");//otherwise, this message is print on serial console
    } 
}

void reconnect() {
  // Loop until we're reconnected to MQTT broker
  espMAC = macToStr(mac);// the MAC address of each ESP8266 is used to uniquely identify nodes
  espMAC.toCharArray(espMAC2,13);
  sprintf(nodefeed, "%s%s", "sensorsfeed/commands/", espMAC2);

  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    if (client.connect("ESP8266Client")) {
      Serial.println("connected");
      client.subscribe(nodefeed);//client subscribe to "sensorsfeed/commands/espMACaddress" feed and listen for commands
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}//end reconnect

void tempread() {

if ( !ds.search(addr)) {
ds.reset_search();
delay(250);
return;
}
// the first ROM byte indicates which chip
switch (addr[0]) {
   case 0x10:
//Serial.println("  Chip = DS18S20");  // or old DS1820
    type_s = 1;
    break;
   case 0x28:
//Serial.println("  Chip = DS18B20");
    type_s = 0;
    break;
  case 0x22:
//Serial.println("  Chip = DS1822");
    type_s = 0;
    break;
  default:
//Serial.println("Device is not a DS18x20 family device.");
  return;
}

ds.reset();
ds.select(addr);
ds.write(0x44); // start conversion
delay(1000);
present = ds.reset();
ds.select(addr);
ds.write(0xBE);         // Read Scratchpad

for ( i = 0; i < 9; i++) {           // we need 9 bytes
data[i] = ds.read();
}

int16_t raw = (data[1] << 8) | data[0];
if (type_s) {
raw = raw << 3; // 9 bit resolution default
if (data[7] == 0x10) {
                      // "count remain" gives full 12 bit resolution
                      raw = (raw & 0xFFF0) + 12 - data[6];
                     }
} 
else {
byte cfg = (data[4] & 0x60);
// at lower res, the low bits are undefined, so let's zero them
if (cfg == 0x00) raw = raw & ~7;  // 9 bit resolution, 93.75 ms
else if (cfg == 0x20) raw = raw & ~3; // 10 bit res, 187.5 ms
else if (cfg == 0x40) raw = raw & ~1; // 11 bit res, 375 ms
//// default is 12 bit resolution, 750 ms conversion time
    }
celsius = (float)raw / 16.0;
//fahrenheit = celsius * 1.8 + 32.0;
}//end tempread

void setup() {
Serial.begin(115200);
// Connect to WiFi network
Serial.print("Connecting to ");
Serial.println(ssid);

WiFi.begin(ssid, password);
while (WiFi.status() != WL_CONNECTED) {
     delay(500);
     Serial.print(".");
     }
Serial.println("");
Serial.println("WiFi connected");

Serial.println(WiFi.localIP());// Print the IP address
WiFi.macAddress(mac);//read own ESP MAC address
client.setServer(mqtt_server, 1883);
client.setCallback(callback);
}

void loop() {

tempread();//read temperature from sensor
//Serial.print("Temperature = ");
//Serial.print(celsius);
//Serial.println(" Celsius, ");

//check for MQTT client connection and attempt reconection if required
if (!client.connected()) {
    reconnect();
}

String espdata = "temp=" + (String)celsius + "=" + (String)espMAC; //string what is going to be sent to MQTT broker running on RaspberryPi
client.loop();
espdata.toCharArray(msg, 50);
Serial.print("Publish message: ");
Serial.println(msg);
client.publish("sensorsfeed/temperature", msg);
client.subscribe(nodefeed);

delay(5000);
}
