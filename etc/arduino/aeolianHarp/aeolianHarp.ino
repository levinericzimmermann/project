
// Software to control aeolian harp (DIY ebows).
//
// Use https://github.com/scandum/rotate
#include "rotate.h"

const unsigned long loopCount = 7;
const int leftRotate = loopCount - 1;

// This array contains all waveforms we can pick from
/*----------------------
const int loopChoiceArray[][10] = {
  // silence
  { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
  // basic
  { 0, 90, 140, 180, 200, 204, 180, 150, 100, 50 },
  // loud :)
  { 0, 255, 255, 255, 255, 255, 255, 255, 255, 255 },
  // basic 2
  { 0, 100, 150, 200, 255, 200, 150, 100, 50, 0 },
  // plucking
  { 255, 255, 255, 254, 254, 254, 253, 253, 253, 253 },
  { 100, 100, 100, 99, 99, 99, 98, 98, 98, 100 },
  { 0, 25, 50, 75, 100, 200, 100, 75, 50, 25 },

};
----------------------*/

const int loopChoiceArray[][7] = {
  // silence
  { 0, 0, 0, 0, 0, 0, 0 },
  // basic
  { 0, 255, 255, 255, 255, 255, 0 },
};



// Set which pins use electromagnets
const int         pinArray[3]             = { 3, 5, 6 };
// This array sets the frequency of each magnet. periodTime is calculated: ((1 / frequency * 1000000) / loopCount)
// Default is 120Hz -> 8333 periodTime
unsigned long     defaultPeriodTime       = 8333 / loopCount;
unsigned long     periodTimeArray[3]      = { defaultPeriodTime, defaultPeriodTime, defaultPeriodTime };
// The last time when the magnet was triggered
unsigned long     lastTimeArray[3]        = { 0, 0, 0 };
// isPlaying actually specifies whether we make a fadein or a fadeout.
bool              isPlayingArray[3]       = { false, false, false };
double            amplitudeFactorArray[3] = { 0, 0, 0 };
// Array of waveforms
/*----------------------
int               loopArray[3][10]        = {
  { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
  { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
  { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
};
----------------------*/
int               loopArray[3][7]        = {
  { 0, 0, 0, 0, 0, 0, 0 },
    { 0, 0, 0, 0, 0, 0, 0 },
  { 0, 0, 0, 0, 0, 0, 0 },
};
// How many magnets exist? 
const int         magnetCount             = sizeof(pinArray) / sizeof(*pinArray);

// Protocoll string
char              msg[256];
int               msgIndex;
const int         msgCount                = 256;

unsigned long     currentTime;

const double riseFactor = 1.1;
const double fallFactor = 0.9;


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
      // ////////////////////////////////////////////////////////////////////
      // START STRING EXECUTION PART
      currentTime = micros();
      int i;
      for (i = 0; i < magnetCount; i++)
      {
        double amplitudeFactor = amplitudeFactorArray[i];
        if (amplitudeFactor > 0) {
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
            // isPlaying actually specifies whether we make a fadein or a fadeout.
            bool isPlaying = isPlayingArray[i];
            int value = loopArray[i][0] * amplitudeFactor;
            // debug
            // Serial.println(difference);
            // Serial.println(value);
            digitalWrite(pinArray[i], value);
            lastTimeArray[i] = currentTime;
            auxiliary_rotation(loopArray[i], 1, leftRotate);
            // Fadein / Fadeout
            double amplitudeFactorFactor;
            if (isPlayingArray[i]) {
              amplitudeFactorFactor = riseFactor;
            } else {
              amplitudeFactorFactor = fallFactor;
            }
            double newAmplitudeFactor = amplitudeFactor * amplitudeFactorFactor;
            if (newAmplitudeFactor > 1) {
              newAmplitudeFactor = 1;
            } else if (newAmplitudeFactor < 0.01) {
              newAmplitudeFactor = 0;
              // The next time the magnet is ignored, because
              // its amplitudeFactor is already 0. So 0 won't
              // be written to the magnet, so it's still a bit
              // on. But we want to safely turn it off.
              digitalWrite(pinArray[i], newAmplitudeFactor);
            }
            amplitudeFactorArray[i] = newAmplitudeFactor;
          }
        }
      }
      // END STRING EXECUTION PART
      // ////////////////////////////////////////////////////////////////////

      // ////////////////////////////////////////////////////////////////////
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
      // ////////////////////////////////////////////////////////////////////

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
      int pinIndex                          = tokenArray[0];
      int mode                              = tokenArray[1];  // 0 = setFrequency; 1 = setLoop
      unsigned long periodTimeOrLoopIndex   = tokenArray[2];

      if (pinIndex >= magnetCount || pinIndex < 0) {
        Serial.print("INVALID PIN INDEX ");
        Serial.println(pinIndex);
        return;
      }

      if (periodTimeOrLoopIndex < 0) {
        Serial.print("INVALID periodTimeOrLoopIndex ");
        Serial.println(periodTimeOrLoopIndex);
        return;
      }

      int pin = pinArray[pinIndex];

      // LOG
      Serial.print("Pin (");
      Serial.print(pin);

      // Execute command
      if (mode == 0) {
        // We need to divide the frequency value by our loopCount,
        // because one loop equals one repeating period e.g. the period
        // size of the frequeny.
        periodTimeOrLoopIndex /= loopCount;
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
          // When setting to 'false', amplitudeFactor
          // is becoming smaller and smaller. When it's
          // small enough it is set to 0 and the magnet
          // stops playing.
          isPlayingArray[pinIndex] = false;
        } else {
          // When setting to 'true', amplitudeFactor is
          // becoming bigger and bigger until it reaches 1.
          // But our loop still ignores our magnet if we
          // don't specify a value which is already bigger
          // than 0. This is why seed the starting value 0.01.
          isPlayingArray[pinIndex] = true;
          amplitudeFactorArray[pinIndex] = 0.01;
        }
      }
   }
}

 
