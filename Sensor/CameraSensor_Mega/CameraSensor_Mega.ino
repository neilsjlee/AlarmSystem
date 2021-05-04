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
#include <Adafruit_VC0706.h>


#define VC0706_TX 2
#define VC0706_RX 3
#define ledPin 4

String DEVICE_ID = "00000002";
String DEVICE_TYPE = "Camera";

//SoftwareSerial cameraconnection(VC0706_TX, VC0706_RX);  // VC0706 Camera Module RX & TX
//Adafruit_VC0706 cam = Adafruit_VC0706(&cameraconnection);

Adafruit_VC0706 cam = Adafruit_VC0706(&Serial2);

//SoftwareSerial MySerial1(8, 9); // Wi-Fi Module ESP-01 RX & TX

PN532_SPI pn532hwspi(SPI, 53);
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
  
  Serial.begin(115200);

  Serial.println(F("VC0706 Camera test"));
  
  // Try to locate the camera
  if (cam.begin()) {
    Serial.println(F("Camera Found:"));
  } else {
    Serial.println(F("No camera found?"));
    //while(true);
  }

  // Print out the camera version information (optional)
  char *reply = cam.getVersion();
  if (reply == 0) {
    Serial.print(F("Failed to get version"));
  } else {
    Serial.println(F("-----------------"));
    Serial.print(reply);
    Serial.println(F("-----------------"));
  }
  // Set the picture size - you can choose one of 640x480, 320x240 or 160x120 
  // Remember that bigger pictures take longer to transmit!
  
  //cam.setImageSize(VC0706_640x480);        // biggest
  cam.setImageSize(VC0706_320x240);        // medium
  //cam.setImageSize(VC0706_160x120);          // small

  // You can read the size back from the camera (optional, but maybe useful?)
  uint8_t imgsize = cam.getImageSize();
  Serial.print(F("Image size: "));
  if (imgsize == VC0706_640x480) Serial.println(F("640x480"));
  if (imgsize == VC0706_320x240) Serial.println(F("320x240"));
  if (imgsize == VC0706_160x120) Serial.println(F("160x120"));

  // Two new functions, 'getAEFlicker' and 'setAEFlicker()' was added to the <Adafruit_VC0706.h> library
  // in order to check the current AE Flicker setting 
  // and change it from 60HZ to 50HZ.
  Serial.print(F("AE Flicker Setting: "));
  Serial.println(cam.getAEFlicker());
  Serial.println(cam.setAEFlicker(0)); // AE Flicker: 50HZ
  Serial.print(F("AE Flicker Setting: "));
  Serial.println(cam.getAEFlicker());

  // Two new functions, 'getAEAutoOrIndoor' and 'setAEAutoOrIndoor()' was added to the <Adafruit_VC0706.h> library
  // in order to check the current AE environment setting 
  // and change it from 'Auto Switch' to 'Force Indoor',
  // because 'Auto Switch' changed the image's brightness so dramatically that it recognized that change as a motion.
  Serial.print(F("AE Auto/Force Indoor Setting: "));
  Serial.println(cam.getAEAutoOrIndoor());
  Serial.println(cam.setAEAutoOrIndoor(1)); // AE Forced Outdoor
  Serial.print(F("AE Auto/Force Indoor Setting: "));
  Serial.println(cam.getAEAutoOrIndoor());

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
    
  Serial3.begin(115200);
  WiFi.init(&Serial3);

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
  //  Motion detection system can alert you when the camera 'sees' motion!
  // cam.setMotionDetect(true);           // turn it on
  cam.setMotionDetect(false);        // turn it off   (default)

  // You can also verify whether motion detection is active!
  Serial.print(F("Motion detection is "));
  if (cam.getMotionDetect()) 
    Serial.println(F("ON"));
  else 
    Serial.println(F("OFF"));

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
    /*
    if (cam.motionDetected() == 1) {
      digitalWrite(ledPin, HIGH);
      Serial.println(F("MOTION DETECTED"));
    }
    else {
      digitalWrite(ledPin, LOW);
      Serial.println(F("MOTION NOT DETECTED"));
    }
    */
    if (cam.motionDetected() == 1) {
      digitalWrite(ledPin, HIGH);
      Serial.print(F("cam.motionDetected(): "));Serial.println(cam.motionDetected());

      if (motionState == false){
        motionState = true;
        cam.setMotionDetect(false);
        Serial.println(F("Motion Detected! Sending POST message to Control Hub."));
        sendAlertPostMessage();
      }
    }
    else {
      // Change the motion state to false (no motion):
      if (motionState == true) {
        Serial.println(F("Motion ended!"));
        Serial.print(F("cam.motionDetected(): "));Serial.println(cam.motionDetected());
        if (! cam.takePicture()) 
          Serial.println("Failed to snap!");
        else 
          Serial.println("Picture taken!");
          
        uint16_t jpglen = cam.frameLength();
        Serial.print(jpglen, DEC);
        Serial.println(F(" byte image"));

        if (client.connect(server_ip, 2002)) {
          Serial.println(F("SENDING POST - Connected to server"));
          client.print(F("POST /cam_photo HTTP/1.1\r\nHost: ")); client.print(String(server_ip)); client.print(F(":2002\r\nAccept: */*\r\nContent-Length: "));
          client.print(jpglen, DEC); client.print(F("\r\nContent-Type: image/jpeg\r\n\r\n"));
          delay(1000);
          while (jpglen > 0) {
            // ****** https://m.blog.naver.com/PostView.nhn?blogId=roboholic84&logNo=220821919602&proxyReferer=https:%2F%2Fwww.google.com%2F
            // read 32 bytes at a time;
            uint8_t *buffer;
            uint8_t bytesToRead = min((uint16_t)32, jpglen); // change 32 to 64 for a speedup but may not work with all setups!
            buffer = cam.readPicture(bytesToRead);
            //imgFile.write(buffer, bytesToRead);
  
            // Serial.print("Read ");  Serial.print(bytesToRead, DEC); Serial.println(" bytes");
            //Serial.write(buffer, bytesToRead);
            
            //client.print(F("{\"device_id\":\"")); client.print(DEVICE_ID); client.println(F("\"}"));
            client.write(buffer, bytesToRead);
    
            jpglen -= bytesToRead;
          }

          
          client.stop();
          Serial.println(F("SENDING POST - Disconnected from server"));
        }

        Serial.println(F("Camera Done"));
        motionState = false;
        
        cam.resumeVideo();
        delay(1000);
        digitalWrite(ledPin, LOW); // Turn off the on-board LED.
        cam.setMotionDetect(true);
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
            cam.setMotionDetect(true);           // turn it on
            Serial.print(F("Motion detection is "));
            if (cam.getMotionDetect()) 
              Serial.println(F("ON"));
            else 
              Serial.println(F("OFF"));
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
        if (buf.endsWith("HTTP")) {
         Serial.println(F("END OF INCOMING MESSAGE"));
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
