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

#define doorLockPin 2
#define keyInputButtonPin 3
#define ledPin 4

String DEVICE_ID = "00000003";
String DEVICE_TYPE = "DoorLock";

SoftwareSerial Serial1(8, 9); // Wi-Fi Module ESP-01 RX & TX

PN532_SPI pn532hwspi(SPI, 10);
SNEP nfc(pn532hwspi);

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
  pinMode(doorLockPin, OUTPUT);
  pinMode(keyInputButtonPin, INPUT_PULLUP);
  
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

  int keyInputButtonRead = digitalRead(keyInputButtonPin);
  if (keyInputButtonRead == 0) {
    Serial.println(F("KEY INPUT BUTTON PRESSED"));
    
    bool nfc_key_result = false;
    nfc_key_result = keyInput();

    if (nfc_key_result){
      Serial.println(F("KEY SUCCESS"));
      armed = !armed;
      if(armed){
        digitalWrite(doorLockPin, HIGH);
        sendLockedPostMessage();
      }
      else{
        digitalWrite(doorLockPin, LOW);
        sendUnlockedPostMessage();
      }
    }
    else{
      Serial.println(F("KEY FAIL"));
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
            digitalWrite(doorLockPin, HIGH);
            uriStart_post = false;
          }
          else if (buf.endsWith("/disarm")){
            Serial.print(F("disarm request received"));
            armed = false;
            digitalWrite(doorLockPin, LOW);
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
        if (buf.endsWith("HTTP")) {
          if (uriStart_get == false){
            Serial.println(F("RESPONDING TO A POST REQUEST"));
            client1.print(F("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection: close\r\n\r\nresponse\":\"ack\"}\r\n"));
            delay(300);
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

bool keyInput(){
  uint8_t ndefBuf[128];
  uint8_t recordBuf[128];
  char str[128] = "";
  int msgSize;
  int counter = 0;
  int compare_result = 0;
  while (counter < 20){ // Abort if there's no NFC Key Input from mobile app within 20 seconds.
    Serial.println(F("Get a message from Android"));
    msgSize = nfc.read(ndefBuf, sizeof(ndefBuf));
    if (msgSize > 0)
    {
      NdefMessage msg  = NdefMessage(ndefBuf, msgSize);
      Serial.println(F("\nSuccess"));
      
      NdefRecord record = msg.getRecord(0);

      record.savePayload(str);
        
      Serial.print(F("Received Key:\t")); Serial.println(str);
      Serial.print(F("Stored Key: \t")); Serial.println(pass);

      // compare_result = strncmp(str, pass, 16);
      for (int i = 0; i < 16; i++){
        if(str[i] != pass[i]){
          compare_result++;
        }
      }
      
      Serial.print(F("Compare Result: \t")); Serial.println(compare_result);
      if(compare_result==0){
        return true;
      }
      else{
        return false;
      }
      break;
    }
    else
    {
      Serial.println(F("receiving failed"));
    }
    delay(1000);
    counter++;
  }
  return false;
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

void sendUnlockedPostMessage(){
  Serial.println();
  Serial.println(F("SENDING POST - Door Unlocked ..."));
  
  if (client.connect(server_ip, 2002)) {
    Serial.println(F("SENDING POST - Connected to server"));
    client.print(F("POST /door_unlocked HTTP/1.1\r\nHost: ")); client.print(String(server_ip)); client.print(F(":2002\r\nAccept: */*\r\nContent-Length: "));
    client.print(String(DEVICE_ID.length()+18)); client.print(F("\r\nContent-Type: application/json\r\n\r\n"));
    client.print(F("{\"device_id\":\"")); client.print(DEVICE_ID); client.println(F("\"}"));
    delay(1000);
    client.stop();
    Serial.println(F("SENDING POST - Disconnected from server"));
  }
}

void sendLockedPostMessage(){
  Serial.println();
  Serial.println(F("SENDING POST - Door Locked ..."));
  
  if (client.connect(server_ip, 2002)) {
    Serial.println(F("SENDING POST - Connected to server"));
    client.print(F("POST /door_locked HTTP/1.1\r\nHost: ")); client.print(String(server_ip)); client.print(F(":2002\r\nAccept: */*\r\nContent-Length: "));
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
