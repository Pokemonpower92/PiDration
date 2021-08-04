/*
    Code for a remote controller 
*/
#include <RF24.h>

struct package {
  unsigned long node;
  unsigned long data;  
};

#define SIG_PIN A0     // Moisture reading from FC-28
#define STATUS_PIN 7   // Status LED 
#define ALERT_PIN 6    // Threshold pin for FC-28

uint64_t address[6] = {0x7878787878LL,
                       0xB3B4B5B6F1LL,
                       0xB3B4B5B6CDLL,
                       0xB3B4B5B6A3LL,
                       0xB3B4B5B60FLL,
                       0xB3B4B5B605LL
                      };

// Globals.
uint64_t ADDR = address[1];
RF24 radio(9, 10);
int threshold;
package p;


void setup(){
    radio.begin();
    Serial.begin(9600);
    pinMode(SIG_PIN, INPUT);
    pinMode(STATUS_PIN, OUTPUT);
    pinMode(ALERT_PIN, INPUT);
    

    pinMode(LED_BUILTIN, OUTPUT);

    radio.openWritingPipe(ADDR);
    radio.stopListening();
    Serial.println("Contoller starting.");

    radio.setPayloadSize(sizeof(p));
    radio.setPALevel(RF24_PA_LOW);
    p.node = 1;
    p.data = 0;
}

void loop(){
    p.data    = analogRead(SIG_PIN);
    threshold = digitalRead(ALERT_PIN);
    
    Serial.print("Analog data: ");
    Serial.println(p.data);

    Serial.print("Threshold: ");
    Serial.println(threshold);

    if(threshold) {
      digitalWrite(STATUS_PIN, LOW);
    }
    else {
      digitalWrite(STATUS_PIN, HIGH);
    }

    radio.write(&p, sizeof(p));
    digitalWrite(LED_BUILTIN, HIGH);
    delay(500);
    digitalWrite(LED_BUILTIN, LOW);
    delay(300000);
}
