
// Software to control aeolian harp (DIY ebows).
//
// Use https://github.com/scandum/rotate
#include "rotate.h"


const unsigned long loopCount = 4;
const int leftRotate = loopCount - 1;

// This array contains all waveforms we can pick from
const int loopChoiceArray[][4] = {
  // silence
  { 0, 0, 0, 0 },
  // basic
  { 120, 254, 120, 0 },
  // basic quiet
  { 0, 20, 250, 20 },
  // basic loud
  { 0, 220, 250, 220 },
  // plucking A
  { 255, 254, 253, 255 },  
  // plucking B
  { 255, 255, 255, 254 },
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
unsigned long     randomMaxArray[3] = { 25, 25, 25 };

// Array of waveforms
int               loopArray[3][4]        = {
  { 0, 0, 0, 0 },
  { 0, 0, 0, 0 },
  { 0, 0, 0, 0 },
};

// How many magnets exist? 
const int         magnetCount             = sizeof(pinArray) / sizeof(*pinArray);

// Protocoll string
char              msg[128];
int               msgIndex;
const int         msgCount                = 128;
bool              msgStarted              = false;
const char        msgDelimiterStart       = '#';
const char        msgDelimiterEnd         = '\n';

unsigned long     currentTime;

// 4 seconds
const unsigned long fadeInDuration = 4000000;
// 5 seconds
const unsigned long fadeOutDuration = 5000000;

double fallFactorArray[3] = { 0.9935, 0.9935, 0.9935 };
double riseFactorArray[3] = { 1.0065, 1.0065, 1.0065 };

const double minAmplitudeFactor = 0.01;
const double maxAmplitudeFactor = 1;
const double fallAmplitudeFactorRatio = minAmplitudeFactor / maxAmplitudeFactor;
const double riseAmplitudeFactorRatio = maxAmplitudeFactor / minAmplitudeFactor;

// Min difference between two micros calls!
// https://www.arduino.cc/reference/en/language/functions/time/micros/
// arduino says 4 to 8 miliseconds precision.
// But the loop frequency is much slower.
// This is
//    (1) because the code takes so long
//    (2) because the baudrate is too low (must be higher)
//
// If we have 5 control points we can represent frequencies up
// to 340Hz with this value. This should be ok.
const unsigned long minPeriodTime = 580;


void setup() {
    // Set up log infos in serial monitor
    Serial.begin(230400);
    // Initialize pins as output
    int i;
    for(i = 0; i < magnetCount; i++)
    {
      pinMode(pinArray[i], OUTPUT);
    }
}

void loop() {
      currentTime = micros();

      // String execution
      int i;
      for (i = 0; i < magnetCount; i++)
      {
        executeString(i, currentTime);
      }

      // Protocoll transmission
      // Basic technique copied from
      // https://makersportal.com/blog/2019/12/15/controlling-arduino-pins-from-the-serial-monitor
      // First collect all characters until we found a line break
      char in_char = ' ';
      while (Serial.available()) {
        in_char = Serial.read();
        if (int(in_char) != -1) {
          if (msgStarted) {
            msg[msgIndex] = in_char;
            msgIndex += 1;
          } else if (in_char==msgDelimiterStart) {
            msgStarted = true;
            if (msg) {
              cleanupMsg();
            }
          }
        }
        if (msgStarted && in_char==msgDelimiterEnd) {
          msgStarted = false;
          Serial.print("Received msg: ");
          Serial.print(msg);
          decodeMsg(msg);
          cleanupMsg();
        }
      }
}


void cleanupMsg() {
    int i;
    // Cleanup: make msg empty, set msgIndex to 0.
    for (i = 0; i < msgCount ; i++) {
      msg[i] = '\0';
    }
    msgIndex = 0;
}


void executeString(int i, unsigned long currentTime) {
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
        long randNumber = random(randomMaxArray[i]);
        int value = (loopArray[i][0] * amplitudeFactor) - randNumber;
        if (value < 0) {
          value = 0;
        }
        // debug
        // Serial.println(difference);
        // Serial.println(value);
        analogWrite(pinArray[i], value);
        lastTimeArray[i] = currentTime;
        auxiliary_rotation(loopArray[i], 1, leftRotate);
        // Fadein / Fadeout
        double amplitudeFactorFactor;
        if (isPlayingArray[i]) {
          amplitudeFactorFactor = riseFactorArray[i];
        } else {
          amplitudeFactorFactor = fallFactorArray[i];
        }
        double newAmplitudeFactor = amplitudeFactor * amplitudeFactorFactor;
        if (newAmplitudeFactor > maxAmplitudeFactor) {
          newAmplitudeFactor = maxAmplitudeFactor;
        } else if (newAmplitudeFactor < minAmplitudeFactor) {
          newAmplitudeFactor = 0;
          // The next time the magnet is ignored, because
          // its amplitudeFactor is already 0. So 0 won't
          // be written to the magnet, so it's still a bit
          // on. But we want to safely turn it off.
          analogWrite(pinArray[i], newAmplitudeFactor);
        }
        amplitudeFactorArray[i] = newAmplitudeFactor;
      }
    }
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

      // Sanity check
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
          setFrequency(pinIndex, periodTimeOrLoopIndex);
      } else {
          setEnvelope(pinIndex, periodTimeOrLoopIndex);
      }
   }
}

void setFrequency(int pinIndex, unsigned long periodTime) {
    Serial.print("): set frequency to ");
    Serial.println(periodTime);
    // We need to divide the frequency value by our loopCount,
    // because one loop equals one repeating period e.g. the period
    // size of the frequeny.
    periodTime /= loopCount;
    if (periodTime < minPeriodTime) {
      periodTime = minPeriodTime;
      Serial.println("WARNING: Received too fast frequency. Autoset to higher freq.");
    }
    periodTimeArray[pinIndex] = periodTime;
    riseFactorArray[pinIndex] = calculateRiseFactor(periodTime);
    fallFactorArray[pinIndex] = calculateFallFactor(periodTime);
}

void setEnvelope (int pinIndex, unsigned long loopIndex) {
    Serial.print("): set envelope to ");
    Serial.println(loopIndex);
    if (loopIndex == 0) {
      // When setting to 'false', amplitudeFactor
      // is becoming smaller and smaller. When it's
      // small enough it is set to 0 and the magnet
      // stops playing.
      isPlayingArray[pinIndex] = false;
    } else {
      isPlayingArray[pinIndex] = true;
      // We only override curve if it's not 0.
      // Otherwise we don't have any fadein/fadeout.
      int i;
      for (i = 0; i < loopCount; i++) {
        loopArray[pinIndex][i] = loopChoiceArray[loopIndex][i];
      }
      // Fadein if not already playing
      if (amplitudeFactorArray[pinIndex] == 0) {
        // When setting to 'true', amplitudeFactor is
        // becoming bigger and bigger until it reaches 1.
        // But our loop still ignores our magnet if we
        // don't specify a value which is already bigger
        // than 0. This is why set the starting seed 0.01.
        amplitudeFactorArray[pinIndex] = minAmplitudeFactor;
      }
    }
}

double calculateFallFactor(unsigned long periodTime) {
    double attackCount = fadeOutDuration / periodTime;
    double fallFactor = pow(fallAmplitudeFactorRatio, 1.0 / attackCount);
    return fallFactor;
}

double calculateRiseFactor(unsigned long periodTime) {
    double attackCount = fadeInDuration / periodTime;
    double riseFactor = pow(riseAmplitudeFactorRatio, 1.0 / attackCount);
    return riseFactor;
}

// Useful for debug
// See: https://forum.arduino.cc/t/printing-a-double-variable/44327/2
void printDouble( double val, unsigned int precision){
// prints val with number of decimal places determine by precision
// NOTE: precision is 1 followed by the number of zeros for the desired number of decimial places
// example: printDouble( 3.1415, 100); // prints 3.14 (two decimal places)

    Serial.print (int(val));  //prints the int part
    Serial.print("."); // print the decimal point
    unsigned int frac;
    if(val >= 0)
      frac = (val - int(val)) * precision;
    else
       frac = (int(val)- val ) * precision;
    int frac1 = frac;
    while( frac1 /= 10 )
        precision /= 10;
    precision /= 10;
    while(  precision /= 10)
        Serial.print("0");

    Serial.println(frac, DEC) ;
}


 
