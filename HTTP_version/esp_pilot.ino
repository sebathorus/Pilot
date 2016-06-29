#include <ESP8266WiFi.h>
#include <OneWire.h>

const char* ssid     = "Your WiFi ssid"; //must use the real ssid and password
const char* password = "Your WiFi Password";
uint8_t mac[6];
String espMAC;

OneWire  ds(2);  // on pin 2 a 4.7K resistor is required between DS18B20 data pin and Vcc
WiFiServer server(80);

String macToStr(const uint8_t* mac)
{
  String result;
  for (int i = 0; i < 6; ++i) {
    result += String(mac[i], 16);
    if (i < 5)
      result += ':';
  }
  return result;
}

void setup() {
Serial.begin(115200);
delay(10);

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

// Start the server
server.begin();
Serial.println("Server started");

// Print the IP address
Serial.println(WiFi.localIP());
}

void loop() {

byte i;
byte present = 0;
byte type_s;
byte data[12];
byte addr[8];
float celsius, fahrenheit;

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
} else {
byte cfg = (data[4] & 0x60);
// at lower res, the low bits are undefined, so let's zero them
if (cfg == 0x00) raw = raw & ~7;  // 9 bit resolution, 93.75 ms
else if (cfg == 0x20) raw = raw & ~3; // 10 bit res, 187.5 ms
else if (cfg == 0x40) raw = raw & ~1; // 11 bit res, 375 ms
//// default is 12 bit resolution, 750 ms conversion time
}
celsius = (float)raw / 16.0;
fahrenheit = celsius * 1.8 + 32.0;
Serial.print("  Temperature = ");
Serial.print(celsius);
Serial.println(" Celsius, ");

WiFiClient client;
const int httpPort = 80;
const char host[] = "192.168.1.xxx";//address of RaspberryPi which host Apache server - must use an existing IP/webserver

if (!client.connect(host, httpPort)) {
    Serial.println("Connection failed...");
    return;
  }

WiFi.macAddress(mac);
espMAC = macToStr(mac);// the MAC address of each ESP8266 is used to uniquely identify nodes
Serial.println(espMAC);
String espdata = "temp=" + (String)celsius + "=" + (String)espMAC; // "temp=" is what is going to be sent using POST to the apache server running on RaspberryPi, see code in add.php
client.println("POST /add.php HTTP/1.1");
client.println("Host: 192.168.1.xxx");
client.println("User-Agent: ESP8266");
client.println("Connection: close");
client.println("Content-Type: application/x-www-form-urlencoded");
client.print("Content-Length: ");
client.println(espdata.length());
client.println();
client.println(espdata);

delay(500);
  
// Read all the lines of the reply from server and print them to Serial
while(client.available()){
    String line = client.readStringUntil('\r');
    Serial.println(line);
  }
  client.stop();

delay(10000);
}
