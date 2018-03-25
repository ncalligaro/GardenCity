//SendReceive.ino
 
#include<SPI.h>
#include<RF24.h>
#include <SimpleDHT.h>

// CE, CSN pins
RF24 radio(9, 10);
int pinDHT22 = A0;
SimpleDHT22 dht22;
SimpleDHT11 dht11;

void setup(void){
//  while(!Serial);
  Serial.begin(115200);
 
  radio.begin();
  radio.setPALevel(RF24_PA_MIN);
  radio.setChannel(0x76);
  radio.openWritingPipe(0xF1F1F0F0E1LL);
  //const uint64_t pipe = (0xE9E9F0F0E1LL);
  const uint64_t pipe = (0xE8E8F0F0E1LL);
  radio.openReadingPipe(1, pipe);
 
  radio.enableDynamicPayloads();
  radio.powerUp();
}
 
void loop(void){
  radio.startListening();
  char receivedMessage[32] = {0};
  
  if(radio.available()){
    Serial.println("Radio Available!");
    radio.read(receivedMessage, sizeof(receivedMessage));
    Serial.println(receivedMessage);
    Serial.println("Turning off the radio.");
    radio.stopListening();
 
    String stringMessage(receivedMessage);
 
    if(stringMessage == "GETREADINGS"){
      //Serial.println("Looks like they want a string!");
      float temperature = 0;
      float humidity = 0;
      int err = SimpleDHTErrSuccess;
      if ((err = dht11.read2(pinDHT22, &temperature, &humidity, NULL)) != SimpleDHTErrSuccess) {
        //Serial.print("Read DHT22 failed, err="); Serial.println(err);delay(1000);
        //return;
        Serial.println("Error reading values from sensor");
        const char errorMsgR[] = "ERROR READING VALUES";
        radio.write(errorMsgR, sizeof(errorMsgR));
      }
      char readings[30];
      String readingsString = "T: " + String(temperature) + " - H: " + String(humidity);
      Serial.println(readingsString);
      readingsString.toCharArray(readings, 30);
      radio.write(readings, sizeof(readings));
      
      Serial.println("We sent our message.");
    } else {
      Serial.println("Unexpected Message");
      Serial.println(stringMessage);
      const char errorMsgM[] = "UNEXPECTED MESSAGE";
      radio.write(errorMsgM, sizeof(errorMsgM));
    }
  }
  delay(100);
 
}
