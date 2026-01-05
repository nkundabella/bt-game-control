#include <Wire.h>
#include <MPU6050.h>
#include <SoftwareSerial.h>

MPU6050 mpu;
SoftwareSerial bt(10, 11);

int joyX = 512;
int joyY = 512;
int buttonState = 1;

void setup() {
  Serial.begin(38400);
  bt.begin(38400);
  Wire.begin();
  mpu.initialize();
  if (!mpu.testConnection()) while (1);
}

void loop() {
  int16_t ax, ay, az;
  mpu.getAcceleration(&ax, &ay, &az);
  joyX = map(ax, -17000, 17000, 0, 1023);
  joyY = map(ay, -17000, 17000, 0, 1023);
  joyX = constrain(joyX, 0, 1023);
  joyY = constrain(joyY, 0, 1023);
  bt.print(joyX);
  bt.print(",");
  bt.print(joyY);
  bt.print(",");
  bt.println(buttonState);
  delay(50);
}
