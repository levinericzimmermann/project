
// Software to control aeolian harp (DIY ebows).
//
// Use https://github.com/scandum/rotate
#include "rotate.h"

const int loopCount = 10;

// This array contains all waveforms we can pick from
const int loopChoiceArray[][10] = {
  // silence
  { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
  // basic
  { 0, 90, 140, 180, 200, 204, 180, 150, 100, 50 },
  // loud :)
  { 0, 255, 255, 255, 255, 255, 255, 255, 255 },
  // basic 2
  { 0, 100, 150, 200, 255, 200, 150, 100, 0 },
  // plucking
  { 255, 255, 255, 254, 254, 254, 253, 253, 253, 253 },
  { 100, 100, 100, 99, 99, 99, 98, 98, 98, 100 },
};

// Set which pins use electromagnets
const int         pinArray[3]             = { 3, 5, 6 };
// This array sets the frequency of each magnet. periodTime is calculated: (1 / frequency * 1000000)
unsigned long     periodTimeArray[3]      = { 8333, 8333, 8333 };
// The last time when the magnet was triggered
unsigned long     lastTimeArray[3]        = { 0, 0, 0 };
bool              isPlayingArray[3]       = { false, false, false };
// Array of waveforms
int               loopArray[3][10]        = {
  { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
  { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
  { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
};
// How many magnets exist? 
const int         magnetCount             = sizeof(pinArray) / sizeof(*pinArray);

// Protocoll string
char              msg[256];
int               msgIndex;
const int         msgCount                = 256;

unsigned long     currentTime;


void setup() {
    // Set up log infos in serial monitor
    Serial.begin(9600);
    // Initialize pins as output
    int i;
    for(i = 0; i < magnetCount; i++)
    {
      pinMode(pinArray[i], OUTPUT);
    }
}

void loop() {
      // /////////////////////////////////
      // START STRING EXECUTION PART
      currentTime = micros();

      int i;
      for (i = 0; i < magnetCount; i++)
      {
        bool  isPlaying   = isPlayingArray[i];
        if (isPlaying) {
          unsigned long   lastTime    = lastTimeArray[i];
          unsigned long   periodTime  = periodTimeArray[i];
          // "micros" resets itself after 70 minutes
          // (see https://www.arduino.cc/reference/en/language/functions/time/micros/)
          // So it could happen that the lastTime looks bigger than the currentTime:
          // in this case set lastTime to 0
          unsigned long   difference;
          if (lastTime > currentTime) {
            difference  = currentTime;
          } else {
            difference  = currentTime - lastTime;
          }

          if (difference > periodTime) {
            int value = loopArray[i][0];
            // debug
            // Serial.println(difference);
            // Serial.println(value);
            digitalWrite(pinArray[i], value);
            lastTimeArray[i] = currentTime;
            auxiliary_rotation(loopArray[i], 1, 9);
          }
        }
      }
      // END STRING EXECUTION PART
      // /////////////////////////////////

      // /////////////////////////////////
      // START PROTOCOL TRANSMISSION PART
      // Basic technique copied from
      // https://makersportal.com/blog/2019/12/15/controlling-arduino-pins-from-the-serial-monitor
      // First collect all characters until we found a line break
      char in_char = ' ';
      while (Serial.available()) {
        in_char = Serial.read();
        if (int(in_char) != -1) {
          msg[msgIndex] = in_char;
          msgIndex += 1;
        }
      }
      if (in_char=='\n') {
        Serial.print("Received msg: ");
        Serial.print(msg);
        decodeMsg(msg);
        // Cleanup: make msg empty, set msgIndex to 0.
        for (i = 0; i < msgCount ; i++) {
          msg[i] = '\0';
        }
        msgIndex = 0;
      }
      // END PROTOCOL TRANSMISSION PART
      // /////////////////////////////////
 }

 
void decodeMsg(char str[]) {
    char* token;
    char* rest = str;
    unsigned long tokenArray[3];
    int tokenIndex = 0;
    while ((token = strtok_r(rest, " ", &rest))) {
      tokenArray[tokenIndex] = strtoul(token, NULL, 10);
      tokenIndex += 1;
    }
    if (tokenIndex != 3) {
      Serial.println("INVALID MSG!");
      return;
    } else {
      int pinIndex                = tokenArray[0];
      int mode                    = tokenArray[1];  // 0 = setFrequency; 1 = setLoop
      int periodTimeOrLoopIndex   = tokenArray[2];

      if (pinIndex >= magnetCount || pinIndex < 0) {
        Serial.print("INVALID PIN INDEX ");
        Serial.println(pinIndex);
        return;
      }

      int pin = pinArray[pinIndex];

      // LOG
      Serial.print("Pin (");
      Serial.print(pin);

      // Execute command
      if (mode == 0) {
        Serial.print("): set frequency to ");
        Serial.println(periodTimeOrLoopIndex);
        periodTimeArray[pinIndex] = periodTimeOrLoopIndex;
      } else {
        Serial.print("): set envelope to ");
        Serial.println(periodTimeOrLoopIndex);
        int i;
        for (i = 0; i < loopCount; i++) {
          loopArray[pinIndex][i] = loopChoiceArray[periodTimeOrLoopIndex][i];
        }
        if (periodTimeOrLoopIndex == 0) {
          isPlayingArray[pinIndex] = false;
        } else {
          isPlayingArray[pinIndex] = true;
        }
      }
   }
}

 
