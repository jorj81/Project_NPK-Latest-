#include <WiFi.h>
#include <WebServer.h>

// ============================================================
// Wi-Fi SETTINGS
// ============================================================

const char* ssid = "Del Rosario Wifi";
const char* password = "delrosariomgapogi";

// Static IP
IPAddress localIP(192, 168, 254, 200);
IPAddress gateway(192, 168, 254, 254);
IPAddress subnet(255, 255, 255, 0);
IPAddress primaryDNS(8, 8, 8, 8);
IPAddress secondaryDNS(8, 8, 4, 4);

// ============================================================
// DEVICE INFORMATION
// ============================================================

// Change this value for every ESP32.
//
// ESP32 #1:
const char* DEVICE_CODE = "ESP32-001";
//
// ESP32 #2:
// const char* DEVICE_CODE = "ESP32-002";
//
// ESP32 #3:
// const char* DEVICE_CODE = "ESP32-003";


// ============================================================
// WEB SERVER
// ============================================================

WebServer server(80);


// ============================================================
// RANDOM SENSOR DATA
// ============================================================

int randomRange(int minVal, int maxVal) {
  return random(minVal, maxVal + 1);
}


// ============================================================
// /data
// ============================================================

void handleData() {

  // Generate fake sensor data
  int soilMoisture = randomRange(30, 90);
  int nitrogen = randomRange(50, 200);
  int phosphorus = randomRange(20, 150);
  int potassium = randomRange(60, 250);

  // Create JSON response
  String json = "{";

  json += "\"device_code\":\"";
  json += DEVICE_CODE;
  json += "\",";

  json += "\"soil_moisture\":";
  json += String(soilMoisture);
  json += ",";

  json += "\"nitrogen\":";
  json += String(nitrogen);
  json += ",";

  json += "\"phosphorus\":";
  json += String(phosphorus);
  json += ",";

  json += "\"potassium\":";
  json += String(potassium);

  json += "}";

  // Send JSON
  server.send(200, "application/json", json);
}


// ============================================================
// NOT FOUND
// ============================================================

void handleNotFound() {

  String json = "{";
  json += "\"error\":\"Not found\",";
  json += "\"device_code\":\"";
  json += DEVICE_CODE;
  json += "\"";
  json += "}";

  server.send(404, "application/json", json);
}


// ============================================================
// CONNECT TO WI-FI
// ============================================================

void connectWiFi() {

  WiFi.mode(WIFI_STA);

  // Configure static IP
  if (!WiFi.config(
        localIP,
        gateway,
        subnet,
        primaryDNS,
        secondaryDNS
      )) {

    Serial.println("Static IP configuration failed");
  }

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);

  Serial.print("Connecting to Wi-Fi");

  while (WiFi.status() != WL_CONNECTED) {

    delay(500);

    Serial.print(".");
  }

  Serial.println();
  Serial.println("Wi-Fi connected");

  Serial.print("Device Code: ");
  Serial.println(DEVICE_CODE);

  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}


// ============================================================
// SETUP
// ============================================================

void setup() {

  Serial.begin(115200);

  delay(1000);

  // Initialize random generator
  randomSeed(analogRead(0));

  // Connect Wi-Fi
  connectWiFi();

  // API endpoint
  server.on("/data", HTTP_GET, handleData);

  // Unknown endpoint
  server.onNotFound(handleNotFound);

  // Start server
  server.begin();

  Serial.println("HTTP server started");
  Serial.println("----------------------------");
  Serial.print("Device Code: ");
  Serial.println(DEVICE_CODE);
  Serial.print("Data URL: http://");
  Serial.print(WiFi.localIP());
  Serial.println("/data");
  Serial.println("----------------------------");
}


// ============================================================
// LOOP
// ============================================================

void loop() {

  server.handleClient();
}