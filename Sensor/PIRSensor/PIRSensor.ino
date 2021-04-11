#include "WiFiEsp.h"
#include <SoftwareSerial.h>
#include <PN532_SWHSU.h>
#include <PN532.h>
#include <PN532_SPI.h>
#include "snep.h"
#include "NdefMessage.h"
#include "SPI.h"
#include <EEPROM.h>
#include <ArduinoJson.h>

#define pirPin 2
#define ledPin 4

String DEVICE_ID = "00000001";
String DEVICE_TYPE = "PIRSensor";

SoftwareSerial Serial1(8, 9); // Wi-Fi Module ESP-01 RX & TX
PN532_SPI pn532hwspi(SPI, 10);
SNEP nfc(pn532hwspi);

int pirSensorRead = 0;
bool motionState = false;
// iPSS = isPreviousSetupSuccessful
char iPSS = 'x';

const char ssid[16] = "";        // your network SSID (name)
const char pass[16] = "";        // your network password
const char server_ip[15] = "";
int status = WL_IDLE_STATUS;     // the Wifi radio's status
String my_ip = "";
bool armed = false;

// Initialize the Ethernet client object
WiFiEspClient client;
WiFiEspServer server(80);

boolean uriStart_post = false;
boolean uriStart_get = false;
boolean received_deregi = false;


void(* resetFunc) (void) = 0;

void setup()
{
  char setting[128] = "";
  int wifi_fail_cnt = 0;

  StaticJsonDocument<200> doc;
  DeserializationError error;
  
  pinMode(ledPin, OUTPUT);
  pinMode(pirPin, INPUT);
  
  Serial.begin(115200);

  /*
  // TEST PURPOSE ONLY - EEPROM RESET
  for(int i = 0; i <129 ; i++){
    EEPROM.write(i, 0);
    Serial.print(EEPROM.read(i));
  }
  Serial.println("");
  */
  
  iPSS = EEPROM.read(128);
  Serial.print(F("EEPROM(128): "));Serial.println(iPSS);
  
  if (iPSS == 'o'){
    for(int i = 0; i <128 ; i++){
      setting[i] = EEPROM.read(i);
    }
  }
  else{
    getSetupDataFromNfc(setting);
  }

  deserializeJson(doc, (const char*)setting);

  if(error){
    Serial.println(F("deserializeJson() failed"));
  }
  else{
    strncpy(ssid, doc["SSID"], 16);
    strncpy(pass, doc["PW"], 16);
    strncpy(server_ip, doc["IP"], 15);
    Serial.print(F("SSID: "));Serial.println(ssid);
    Serial.print(F("PW: "));Serial.println(pass);
    Serial.print(F("IP: "));Serial.println(server_ip);
  }
    
  Serial1.begin(9600);
  WiFi.init(&Serial1);

  // check for the presence of the shield
  if (WiFi.status() == WL_NO_SHIELD) {
    Serial.println(F("WiFi shield not present"));
    // don't continue
    while (true);
  }
  
  // attempt to connect to WiFi network
  while ( status != WL_CONNECTED) {
    if(wifi_fail_cnt < 5){
      Serial.print(F("Attempting to connect to WPA SSID: "));
      Serial.println(ssid);
      // Connect to WPA/WPA2 network
      status = WiFi.begin(ssid, pass);
      wifi_fail_cnt++;
    }
    else{
      if (iPSS == 'o'){
        // This means that it tried to connect Wi-Fi using the previous setting, but it failed. Need to discard the previous setting.
        for(int i = 0; i < 129 ; i ++){
          EEPROM.write(i, 0);
        }
      }
      Serial.println(F("RESET THE SYSTEM"));
      resetFunc(); // Reset the system 
      Serial.println(F("This line should never be called."));
      while(true);
    }
  }

  if(iPSS != 'o'){
    for(int i = 0; i < 128 ; i ++){
      Serial.print(setting[i]);
      EEPROM.write(i, setting[i]);
    }
    EEPROM.write(128, 'o');
  }

  // you're connected now, so print out the data
  Serial.println(F("You're connected to the network"));
  printWifiStatus();

  Serial.println();

  delay(5000);
  
  server.begin();

  delay(5000);

  sendRegisterPostMessage();
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

  if(armed){
    pirSensorRead = digitalRead(pirPin);

    if (pirSensorRead == HIGH) {
      Serial.print(F("ARMED? "));
      Serial.println(armed);
      digitalWrite(ledPin, HIGH);
      delay(150);

      if (motionState == false){
        Serial.println(F("Motion Detected! Sending POST message to Control Hub."));
        sendAlertPostMessage();
        motionState = true;
      }
    }
    else {
      digitalWrite(ledPin, LOW); // Turn off the on-board LED.
      delay(150);
      // Change the motion state to false (no motion):
      if (motionState == true) {
        Serial.println(F("Motion ended!"));
        motionState = false;
      }
    }
  }

  WiFiEspClient client1 = server.available();
  if(client1){
    Serial.println(F("NEW CLIENT"));
    RingBuffer buf(8);
    buf.init();

    while(client1.connected()){
      if(client1.available()){
        char ch = client1.read();
        buf.push(ch);
        Serial.print(ch);
        if (buf.endsWith("POST ")) {
          uriStart_post = true;
        }
        if (uriStart_post){
          if (buf.endsWith("/arm")){
            Serial.print(F("arm request received"));
            armed = true;
            uriStart_post = false;
          }
          else if (buf.endsWith("/disarm")){
            Serial.print(F("disarm request received"));
            armed = false;
            uriStart_post = false;
          }
          else if (buf.endsWith("/deregi")){
            Serial.print(F("deregister request received"));
            uriStart_post = false;
            received_deregi = true;
          }
          else if (buf.endsWith("HTTP")){
            Serial.print(F("Unknown URI"));
            uriStart_post = false;
          }
        }
        if (buf.endsWith("GET ")) {
          uriStart_get = true;
        }
        if (buf.endsWith("\r\n\r\n")) {
          if (uriStart_get == false){
            Serial.println(F("RESPONDING TO A POST REQUEST"));
            client1.print(F("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection: close\r\n\r\nresponse\":\"ack\"}\r\n"));
            delay(150);
            client1.stop();
            Serial.println(F("NEW CLIENT STOP"));
            if(received_deregi){
              EEPROM.write(128, 'x');
              resetFunc(); // Reset the system
            }
          }
          else{
            Serial.println(F("RESPONDING TO A GET REQUEST"));
            client1.println(F("HTTP/1.1 200 OK"));
            client1.println(F("Content-Type: text/html"));
            client1.println(F("Connection: close"));
            client1.println();
            if(armed)
              client1.print(F("{\"armed\": true}"));
            else
              client1.print(F("{\"armed\": false}"));
            uriStart_get = false;
          }
          client1.stop();
          break;
        }
      }
    }
  }
}

void getSetupDataFromNfc(char* str){
  uint8_t ndefBuf[128];
  uint8_t recordBuf[128];
  int msgSize;
  while (true){
    Serial.println(F("Get a message from Android"));
    msgSize = nfc.read(ndefBuf, sizeof(ndefBuf));
    if (msgSize > 0)
    {
      NdefMessage msg  = NdefMessage(ndefBuf, msgSize);
      Serial.println(F("\nSuccess"));
      
      NdefRecord record = msg.getRecord(0);

      record.savePayload(str);
        
      Serial.print(F("Result: "));
      Serial.println(str);

      break;
    }
    else
    {
      Serial.println(F("receiving failed"));
    }
    delay(1000);
  }
}

void printWifiStatus()
{
  // print the SSID of the network you're attached to
  Serial.print(F("SSID: "));
  Serial.println(WiFi.SSID());

  // print your WiFi shield's IP address
  IPAddress t_my_ip = WiFi.localIP();
  my_ip = String() + t_my_ip[0] + "." + t_my_ip[1] + "." + t_my_ip[2] + "." + t_my_ip[3];
  
  Serial.print(F("IP Address: "));
  Serial.println(my_ip);

  // print the received signal strength
  long rssi = WiFi.RSSI();
  Serial.print(F("Signal strength (RSSI):"));
  Serial.print(rssi);
  Serial.println(" dBm");
}

void sendAlertPostMessage(){
  Serial.println();
  Serial.println(F("SENDING POST - ALERT ..."));
  
  if (client.connect(server_ip, 2002)) {
    Serial.println(F("SENDING POST - Connected to server"));
    client.print(F("POST /alert HTTP/1.1\r\nHost: ")); client.print(String(server_ip)); client.print(F(":2002\r\nAccept: */*\r\nContent-Length: "));
    client.print(String(DEVICE_ID.length()+18)); client.print(F("\r\nContent-Type: application/json\r\n\r\n"));
    client.print(F("{\"device_id\":\"")); client.print(DEVICE_ID); client.println(F("\"}"));
    delay(1000);
    client.stop();
    Serial.println(F("SENDING POST - Disconnected from server"));
  }
}

void sendRegisterPostMessage() {
  Serial.println();
  Serial.println(F("SENDING POST- REGISTER ..."));
  
  if (client.connect(server_ip, 2002)) {
    Serial.println(F("SENDING POST - Connected to server"));
    client.print(F("POST /register HTTP/1.1\r\nHost: ")); client.print(String(server_ip)); client.print(F(":2002\r\nAccept: */*\r\nContent-Length: "));
    client.print(String(DEVICE_ID.length()+DEVICE_TYPE.length()+my_ip.length()+41)); client.print(F("\r\nContent-Type: application/json\r\n\r\n"));
    client.print(F("{\"device_id\":\"")); client.print(DEVICE_ID); client.print(F("\",\"device_type\":\"")); client.print(DEVICE_TYPE); client.print(F("\",\"ip\":\"")); client.print(my_ip); client.println(F("\"}"));
    delay(1000);
    client.stop();
    Serial.println(F("SENDING POST - Disconnected from server"));
  }
}
