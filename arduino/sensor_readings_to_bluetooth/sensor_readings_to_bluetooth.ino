#include <DHT.h>
#include "Ultrasonic.h"
#include <SoftwareSerial.h>

#define RxD 8    
#define TxD 9
#define DHTPIN A3
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);
Ultrasonic ultrasonic(4);
SoftwareSerial blueToothSerial(RxD, TxD);

void setup() {
  // Put your setup code here, to run once:
  Serial.begin(9600);

  while(!Serial) { ; }
  Serial.println("Started");

  dht.begin();
  setupBlueToothConnection();
  
  // Flushes any residual data from the serial buffers.
  Serial.flush();
  blueToothSerial.flush();

}

void loop() {
  // Put your main code here, to run repeatedly:

  // Checks if a Bluetooth connection is available.
  if (blueToothSerial.available() > 0) {
    char incoming = blueToothSerial.read();
    Serial.print(incoming);
  }

  // Variables for sensor readings.
  float temp = dht.readTemperature();
  float humid = dht.readHumidity();
  long range = ultrasonic.MeasureInInches();

  // Readings to be sent via Bluetooth in JSON format. 
  blueToothSerial.print("{\"temperature\":");
  blueToothSerial.print(temp);
  blueToothSerial.print(", \"humidity\":");
  blueToothSerial.print(humid);
  blueToothSerial.print(", \"distance\":");
  blueToothSerial.print(range);
  blueToothSerial.println("}");

  // 2 second delay between readings.
  delay(2000);
}

void setupBlueToothConnection()
{
  // Begins a software serial session at 9600 baud for the Bluetooth module.
  blueToothSerial.begin(9600);

  // Sends a series of AT commands to configure the BLE module.
  blueToothSerial.print("AT");
  delay(2000);

  // Sets the module’s baud rate to 9600 (AT+BAUD4 typically means 9600).
  blueToothSerial.print("AT+BAUD4");
  delay(2000);

  // Set the module’s role to “S” (often means slave/peripheral).
  blueToothSerial.print("AT+ROLES");
  delay(2000);

  // Assigns the name FoodLink.
  blueToothSerial.print("AT+NAMESFoodLink");
  delay(2000);

  // Enables authentication (AT+AUTH1).
  blueToothSerial.print("AT+AUTH1");
  delay(2000);

  // Flushes any residual data from the software serial buffer.
  blueToothSerial.flush();
  Serial.println("Finished Bluetooth Setup");
}

