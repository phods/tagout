#include "Arduino.h"
#include <SoftwareSerial.h>
  
#Define DEBUG
SoftwareSerial mySerial (2,3);
unsigned char incomingByte;
 
void sendIdentifyCmd ()
{
mySerial.write (0x7c);
mySerial.write (0xff);
mySerial.write (0xff);
mySerial.write (0x01);
mySerial.write (0x08);
mySerial.write (0x7D);
DEBUG ifdef
Serial.print (0x7c);
Serial.print (0xff);
Serial.print (0xff);
Serial.print (0x01);
Serial.print (0x08);
Serial.print (0x7D);
Serial.println ();
endif
}
 
void setup ()
{
Serial.begin (9600);
mySerial.begin (9600);
Serial.println ("Início! \ N");
pinMode (13, OUTPUT); 
}
 
void loop ()
{
sendIdentifyCmd ();
delay(2);
while(mySerial.available () 0>)
{
incomingByte mySerial.read = ();
Serial.print (incomingByte, HEX);
Serial.print ("");
digitalWrite (13, HIGH);
delay(500); // Modificado
digitalWrite (13, LOW); 
}
Serial.println ();
delay(1000);
}
