/*
 WiFiEsp example: WebClient
 This sketch connects to google website using an ESP8266 module to
 perform a simple web search.
 For more details see: http://yaab-arduino.blogspot.com/p/wifiesp-example-client.html
*/

#include "WiFiEsp.h"

#ifndef HAVE_HWSERIAL1
#include "SoftwareSerial.h"

#define pirPin 2
#define ledPin 4

SoftwareSerial Serial1(8, 9); // RX, TX
#endif

int pirSensorRead = 0;
bool motionState = false;

char ssid[] = "ATTb3hjRMS";            // your network SSID (name)
char pass[] = "kz7hwdt7jtpy";        // your network password
int status = WL_IDLE_STATUS;     // the Wifi radio's status

char server[] = "192.168.1.89";

int cnt=0;
int interval = 5000;
unsigned long previousMillis = 0;


// Initialize the Ethernet client object
WiFiEspClient client;

void setup()
{
  pinMode(ledPin, OUTPUT);
  pinMode(pirPin, INPUT);
  
  // initialize serial for debugging
  Serial.begin(115200);
  // initialize serial for ESP module
  Serial1.begin(9600);
  // initialize ESP module
  WiFi.init(&Serial1);

  // check for the presence of the shield
  if (WiFi.status() == WL_NO_SHIELD) {
    Serial.println("WiFi shield not present");
    // don't continue
    while (true);
  }

  // attempt to connect to WiFi network
  while ( status != WL_CONNECTED) {
    Serial.print("Attempting to connect to WPA SSID: ");
    Serial.println(ssid);
    // Connect to WPA/WPA2 network
    status = WiFi.begin(ssid, pass);
  }

  // you're connected now, so print out the data
  Serial.println("You're connected to the network");

  printWifiStatus();

  Serial.println();
}

void loop()
{
  unsigned long currentMillis = millis();

  // if there are incoming bytes available
  // from the server, read them and print them
  while (client.available()) {
    char c = client.read();
    Serial.write(c);
  }

  pirSensorRead = digitalRead(pirPin);

  if (pirSensorRead == HIGH) {
    digitalWrite(ledPin, HIGH);
    delay(150);

    if (motionState == false){
      Serial.println("Motion Detected! Sending POST message to Control Hub.");
      sendTestPostMessage();
      motionState = true;
    }
  }
  else {
    digitalWrite(ledPin, LOW); // Turn off the on-board LED.
    delay(150);
    // Change the motion state to false (no motion):
    if (motionState == true) {
      Serial.println("Motion ended!");
      motionState = false;
    }
  }  

  
//  if (currentMillis - previousMillis > interval){
//    previousMillis = currentMillis;
//    
//  }
//  
//  // if the server's disconnected, stop the client
//  if (!client.connected()) {
//    Serial.println();
//    Serial.println("Disconnecting from server...");
//    client.stop();
//
//    // do nothing forevermore
//    while (true);
//  }
  
}


void printWifiStatus()
{
  // print the SSID of the network you're attached to
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  // print your WiFi shield's IP address
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);

  // print the received signal strength
  long rssi = WiFi.RSSI();
  Serial.print("Signal strength (RSSI):");
  Serial.print(rssi);
  Serial.println(" dBm");
}


void sendTestPostMessage(){
    Serial.println();
    Serial.println("Starting connection to server...");
    // if you get a connection, report back via serial
  if (client.connect(server, 2002)) {
    Serial.println("Connected to server");
    // Make a HTTP request
    //String content = "Hello from Arduino";
    //client.println("POST /alert HTTP/1.1");
    //client.println("Host: 192.168.1.89:2002");
    //client.println("Accept: */*");
    //client.println("Content-Length: " + String(content.length()));
    ////client.println("Content-Type: application/x-www-form-urlencoded");
    //client.println("Content-Type: text/plain");
    //client.println();
    //client.println(content);
    int value = 2.5;  // an arbitrary value for testing
    String content = "{\"JSON_key\": " + String(value) + "}";
    client.println("POST /alert HTTP/1.1");
    client.println("Host: 198.168.1.89:2002");
    client.println("Accept: */*");
    client.println("Content-Length: " + String(content.length()));
    client.println("Content-Type: application/json");
    client.println();
    client.println(content);
  }
}
