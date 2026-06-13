#include <WiFi.h>
#include <PubSubClient.h>

const char* ssid = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";
const char* mqtt_server = "broker.hivemq.com"; // Free public broker

WiFiClient espClient;
PubSubClient client(espClient);

#define TRIG_PIN 5
#define ECHO_PIN 18
#define RED_LED 21
#define GREEN_LED 22
#define BUZZER 19

const int BIN_HEIGHT = 50; // ডাস্টবিনের মোট উচ্চতা সে.মি. তে

void setup() {
  Serial.begin(115200);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(RED_LED, OUTPUT);
  pinMode(GREEN_LED, OUTPUT);
  pinMode(BUZZER, OUTPUT);

  setup_wifi();
  client.setServer(mqtt_server, 1883);
}

void setup_wifi() {
  delay(10);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
}

void reconnect() {
  while (!client.connected()) {
    if (client.connect("ESP32_SmartBin_01")) {
      Serial.println("MQTT Connected");
    } else {
      delay(5000);
    }
  }
}

void loop() {
  if (!client.connected()) reconnect();
  client.loop();

  long duration;
  int distance;
  
  digitalWrite(TRIG_PIN, LOW); delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH); delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  
  duration = pulseIn(ECHO_PIN, HIGH);
  distance = duration * 0.034 / 2;

  // Fill Percentage Calculation
  int fill_percentage = ((BIN_HEIGHT - distance) * 100) / BIN_HEIGHT;
  if (fill_percentage < 0) fill_percentage = 0;
  if (fill_percentage > 100) fill_percentage = 100;

  String status = "Empty";

  if (fill_percentage > 85) {
    digitalWrite(RED_LED, HIGH);
    digitalWrite(GREEN_LED, LOW);
    digitalWrite(BUZZER, HIGH);
    status = "Full Alert!";
  } else {
    digitalWrite(RED_LED, LOW);
    digitalWrite(GREEN_LED, HIGH);
    digitalWrite(BUZZER, LOW);
    status = "Normal";
  }

  // JSON Payload
  String payload = "{\"bin_id\": \"BIN_01\", \"fill_percent\": " + String(fill_percentage) + ", \"status\": \"" + status + "\"}";
  client.publish("smartcity/waste/bin1", payload.c_str());

  delay(5000); // Send data every 5 seconds
}