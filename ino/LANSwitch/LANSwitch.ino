/*
 * Send a HTTP POST to a server on the LAN when a switch is pressed
 */
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

//wifi setup
const char* ssid = "YOURSSID";
const char* password = "PASSWORD";

// not actually used - currently hard coded in the POST - feel free to improve
// find/replace "YOURHOSTIP" and "LIGHT_NAME" for your own purposes
const char* host = "YOURHOSTIP"; 
const uint16_t port = 7990;
const char* path = "/lights";
String light = "LIGHT_NAME";

// set the pin your button is attached to
#define buttonPin 14

boolean buttonState = LOW;
unsigned long onTime;
#define LEDPIN LED_BUILTIN

void setup() {
  Serial.begin(115200);
  pinMode( LEDPIN, OUTPUT );
  delay(10);
  
  pinMode(buttonPin, INPUT_PULLUP);

  Serial.print("Connecting to ");
  Serial.println(ssid);
  IPAddress ip(192, 168, 1, 210); //this device IP
  IPAddress gateway(192, 168, 1, 1);
  IPAddress subnet(255, 255, 255, 0);
  WiFi.config(ip, gateway, subnet);
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
  
  // Print the IP address
  Serial.println(WiFi.localIP());

}

void loop() {
  // read the state of the pushbutton value:
  int b = checkButton();
  buttonState = digitalRead(buttonPin);

  // check if the pushbutton is pressed. If it is, the buttonState is HIGH:
  if (b == 0) {
    digitalWrite(LEDPIN, LOW);
  }
  if (b == 1) lightToggle();
  if (b == 2) lightFull();
  while (b == 3) {
    Serial.println(b);
    b = lightDim();
  }
  // turn LED off:

  if (b != 0) {
    Serial.println(b);
  }
}

void lightToggle() {
  digitalWrite(LEDPIN, HIGH);
  HTTPClient http;

  http.begin("http://YOURHOSTIP:7990/lights");
  http.addHeader("Content-Type", "application/x-www-form-urlencoded");
  int httpCode = http.POST("light=LIGHT_NAME");
  String payload = http.getString();

  Serial.println(httpCode);
  Serial.println(payload);

}

void lightFull() {
  digitalWrite(LEDPIN, HIGH);
  HTTPClient http;

  http.begin("http://YOURHOSTIP:7990/lights");
  http.addHeader("Content-Type", "application/x-www-form-urlencoded");
  int httpCode = http.POST("light=LIGHT_NAME&level=full");
  String payload = http.getString();

  Serial.println(httpCode);
  Serial.println(payload);

}

int lightDim() {
  int retVal;
  onTime = millis();
  digitalWrite(LEDPIN, HIGH);
  buttonState = digitalRead(buttonPin);

  if (buttonState == HIGH) {
    retVal = 0;
  } else {
    retVal = 3;
    HTTPClient http;

    http.begin("http://YOURHOSTIP:7990/lights");
    http.addHeader("Content-Type", "application/x-www-form-urlencoded");
    if (onTime % 700 == 0) {
      int httpCode = http.POST("light=LIGHT_NAME&dim=true");
      String payload = http.getString();

      Serial.println(httpCode);
      Serial.println(payload);
    }
  }
  return retVal;
}

